//! Discord RPC over local IPC.
//!
//! The module talks to the desktop Discord client through its local IPC named
//! pipe. Secrets are loaded only inside pc-server and are never included in
//! command responses.

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::fs;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

const DEFAULT_ENV_PATH: &str = r"C:\Users\kohak\programs\pc_ellie\.env";
const DEFAULT_TOKENS_PATH: &str = r"C:\Users\kohak\programs\pc_ellie2\discord_tokens.json";
const TOKEN_ENDPOINT: &str = "https://discord.com/api/oauth2/token";
const REDIRECT_URI: &str = "http://localhost:8080/oauth/callback";
const DISCORD_RPC_SCOPES: &[&str] = &[
    "rpc",
    "rpc.voice.read",
    "rpc.voice.write",
    "rpc.activities.write",
    "rpc.notifications.read",
    "rpc.screenshare.read",
    "rpc.screenshare.write",
    "rpc.video.read",
    "rpc.video.write",
    "identify",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u32)]
#[allow(dead_code)]
pub enum OpCode {
    Handshake = 0,
    Frame = 1,
    Close = 2,
    Ping = 3,
    Pong = 4,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct DiscordConfig {
    client_id: String,
    client_secret: Option<String>,
    token_endpoint: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct TokenFile {
    access_token: String,
    #[serde(default)]
    refresh_token: Option<String>,
    #[serde(default)]
    scope: Option<String>,
    #[serde(default)]
    token_type: Option<String>,
    #[serde(default)]
    expires_in: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelCandidate {
    pub id: String,
    pub name: String,
    pub channel_type: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GuildCandidate {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub channels: Vec<ChannelCandidate>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct JoinByNameRequest {
    guild_name: String,
    #[serde(default)]
    channel_name: Option<String>,
}

pub fn handle_status() -> Value {
    let config = load_config();
    let tokens = load_tokens();
    let pipe_available = find_pipe_path().is_some();

    json!({
        "status": if config.is_ok() && tokens.is_ok() && pipe_available { "ok" } else { "degraded" },
        "action": "discord_status",
        "pipe_available": pipe_available,
        "config_loaded": config.is_ok(),
        "tokens_loaded": tokens.is_ok(),
        "scopes": tokens.as_ref().ok().and_then(|t| t.scope.clone()).unwrap_or_default(),
        "missing": status_missing(config.as_ref().err(), tokens.as_ref().err(), pipe_available),
    })
}

pub fn handle_json_command(action: &str, params: &str) -> Value {
    let parsed = parse_params(params);
    match action {
        "status" => handle_status(),
        "get_guilds" => rpc_simple("GET_GUILDS", json!({})),
        "get_selected_voice_channel" => rpc_simple("GET_SELECTED_VOICE_CHANNEL", json!({})),
        "get_voice_settings" => rpc_simple("GET_VOICE_SETTINGS", json!({})),
        "get_guild" => {
            let guild_id = get_string(&parsed, "guild_id");
            if guild_id.is_empty() {
                return error("validation_error", "guild_id is required");
            }
            rpc_simple("GET_GUILD", json!({ "guild_id": guild_id }))
        }
        "get_channels" => {
            let guild_id = get_string(&parsed, "guild_id");
            if guild_id.is_empty() {
                return error("validation_error", "guild_id is required");
            }
            rpc_simple("GET_CHANNELS", json!({ "guild_id": guild_id }))
        }
        "select_text_channel" => {
            let channel_id = get_string(&parsed, "channel_id");
            if channel_id.is_empty() {
                return error("validation_error", "channel_id is required");
            }
            rpc_simple("SELECT_TEXT_CHANNEL", json!({ "channel_id": channel_id }))
        }
        "join_voice_channel" => {
            let channel_id = get_string(&parsed, "channel_id");
            if channel_id.is_empty() {
                return error("validation_error", "channel_id is required");
            }
            rpc_simple("SELECT_VOICE_CHANNEL", json!({ "channel_id": channel_id }))
        }
        "leave_voice_channel" => {
            rpc_simple("SELECT_VOICE_CHANNEL", json!({ "channel_id": Value::Null }))
        }
        "set_voice_settings" => rpc_simple("SET_VOICE_SETTINGS", parsed),
        "set_activity" => {
            let mut args = parsed;
            if let Value::Object(map) = &mut args {
                map.entry("pid".to_string())
                    .or_insert_with(|| json!(std::process::id()));
            }
            rpc_simple("SET_ACTIVITY", args)
        }
        "join_voice_by_name" => join_voice_by_name(parsed),
        "unsupported_send_message" => error(
            "unsupported_by_discord_rpc",
            "Discord RPC over IPC does not support arbitrary message or DM sending.",
        ),
        _ => error(
            "unknown_discord_command",
            format!("Unknown Discord RPC command: {action}"),
        ),
    }
}

pub fn encode_frame(opcode: OpCode, payload: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(8 + payload.len());
    out.extend_from_slice(&(opcode as u32).to_le_bytes());
    out.extend_from_slice(&(payload.len() as u32).to_le_bytes());
    out.extend_from_slice(payload);
    out
}

pub fn decode_frame_header(header: &[u8]) -> Result<(u32, u32), String> {
    if header.len() != 8 {
        return Err("Discord IPC frame header must be exactly 8 bytes".into());
    }
    let op = u32::from_le_bytes(header[0..4].try_into().map_err(|_| "invalid opcode")?);
    let len = u32::from_le_bytes(header[4..8].try_into().map_err(|_| "invalid length")?);
    Ok((op, len))
}

pub fn resolve_voice_channel(
    guilds: &[GuildCandidate],
    guild_name: &str,
    channel_name: Option<&str>,
) -> Result<(GuildCandidate, ChannelCandidate), Value> {
    let guild_matches: Vec<GuildCandidate> = guilds
        .iter()
        .filter(|g| normalized_contains(&g.name, guild_name))
        .cloned()
        .collect();

    if guild_matches.is_empty() {
        return Err(json!({
            "status": "not_found",
            "reason": "No matching Discord guild/server was found.",
            "candidates": guilds.iter().map(|g| json!({"id": g.id, "name": g.name})).collect::<Vec<_>>(),
        }));
    }
    if guild_matches.len() > 1 {
        return Err(json!({
            "status": "ambiguous",
            "reason": "Multiple Discord guilds matched.",
            "candidates": guild_matches.iter().map(|g| json!({"id": g.id, "name": g.name})).collect::<Vec<_>>(),
        }));
    }

    let guild = guild_matches[0].clone();
    let voice_channels: Vec<ChannelCandidate> = guild
        .channels
        .iter()
        .filter(|c| is_voice_channel(c.channel_type))
        .cloned()
        .collect();

    if voice_channels.is_empty() {
        return Err(json!({
            "status": "not_found",
            "reason": "The matched guild has no voice channels visible through Discord RPC.",
            "guild": {"id": guild.id, "name": guild.name},
        }));
    }

    let selected = if let Some(name) = channel_name.filter(|s| !s.trim().is_empty()) {
        let channel_matches: Vec<ChannelCandidate> = voice_channels
            .iter()
            .filter(|c| normalized_contains(&c.name, name))
            .cloned()
            .collect();
        if channel_matches.is_empty() {
            return Err(json!({
                "status": "not_found",
                "reason": "No matching voice channel was found.",
                "guild": {"id": guild.id, "name": guild.name},
                "candidates": voice_channels,
            }));
        }
        if channel_matches.len() > 1 {
            return Err(json!({
                "status": "ambiguous",
                "reason": "Multiple voice channels matched.",
                "guild": {"id": guild.id, "name": guild.name},
                "candidates": channel_matches,
            }));
        }
        channel_matches[0].clone()
    } else {
        voice_channels[0].clone()
    };

    Ok((guild, selected))
}

fn join_voice_by_name(params: Value) -> Value {
    let request: JoinByNameRequest = match serde_json::from_value::<JoinByNameRequest>(params) {
        Ok(req) if !req.guild_name.trim().is_empty() => req,
        _ => return error("validation_error", "guild_name is required"),
    };

    let guilds_response = match rpc_value("GET_GUILDS", json!({})) {
        Ok(value) => value,
        Err(value) => return value,
    };
    let guilds = match guilds_from_rpc_response(&guilds_response) {
        Ok(guilds) => guilds,
        Err(value) => return value,
    };

    let matching_guilds: Vec<GuildCandidate> = guilds
        .into_iter()
        .filter(|guild| normalized_contains(&guild.name, &request.guild_name))
        .collect();
    if matching_guilds.is_empty() {
        return json!({
            "status": "not_found",
            "reason": "No matching Discord guild/server was found.",
        });
    }
    if matching_guilds.len() > 1 {
        return json!({
            "status": "ambiguous",
            "reason": "Multiple Discord guilds matched.",
            "candidates": matching_guilds.iter().map(|g| json!({"id": g.id, "name": g.name})).collect::<Vec<_>>(),
        });
    }

    let mut enriched = Vec::new();
    for mut guild in matching_guilds {
        if let Ok(detail) = rpc_value("GET_CHANNELS", json!({ "guild_id": guild.id })) {
            guild.channels = channels_from_guild(&detail);
        }
        enriched.push(guild);
    }

    let (guild, channel) = match resolve_voice_channel(
        &enriched,
        &request.guild_name,
        request.channel_name.as_deref(),
    ) {
        Ok(result) => result,
        Err(value) => return value,
    };

    match rpc_value("SELECT_VOICE_CHANNEL", json!({ "channel_id": channel.id })) {
        Ok(result) => json!({
            "status": "ok",
            "action": "discord_join_voice_by_name",
            "guild": {"id": guild.id, "name": guild.name},
            "channel": {"id": channel.id, "name": channel.name, "type": channel.channel_type},
            "rpc_result": sanitize_rpc_result(result),
        }),
        Err(value) => value,
    }
}

fn rpc_simple(command: &str, args: Value) -> Value {
    match rpc_value(command, args) {
        Ok(value) => json!({
            "status": "ok",
            "action": command,
            "result": sanitize_rpc_result(value),
        }),
        Err(value) => value,
    }
}

fn rpc_value(command: &str, args: Value) -> Result<Value, Value> {
    let mut client = match DiscordIpcClient::connect() {
        Ok(client) => client,
        Err(e) => return Err(error("discord_ipc_unavailable", e)),
    };
    if let Err(e) = client.handshake_and_authenticate() {
        return Err(error("discord_authentication_failed", e));
    }
    client
        .send_command(command, args)
        .map_err(|e| error("discord_rpc_error", e))
}

struct DiscordIpcClient {
    stream: Box<dyn ReadWrite>,
}

trait ReadWrite: Read + Write {}
impl<T: Read + Write> ReadWrite for T {}

impl DiscordIpcClient {
    fn connect() -> Result<Self, String> {
        open_first_pipe().map(|stream| Self { stream })
    }

    fn handshake_and_authenticate(&mut self) -> Result<(), String> {
        let config = load_config()?;
        let mut tokens = load_tokens()?;
        let handshake = json!({ "v": 1, "client_id": config.client_id });
        self.write_frame(OpCode::Handshake, &handshake)?;
        let _ = self.read_frame()?;

        let auth = self.send_command(
            "AUTHENTICATE",
            json!({ "access_token": tokens.access_token }),
        )?;
        if rpc_has_error(&auth) {
            match refresh_tokens(&config, &tokens) {
                Ok(new_tokens) => {
                    tokens = new_tokens;
                    let retry = self.send_command(
                        "AUTHENTICATE",
                        json!({ "access_token": tokens.access_token }),
                    )?;
                    if rpc_has_error(&retry) {
                        return Err("Discord rejected the refreshed OAuth token.".into());
                    }
                    return Ok(());
                }
                Err(refresh_error) => {
                    self.reconnect_and_handshake(&config.client_id)?;
                    match self.authorize_exchange_and_authenticate(&config) {
                        Ok(()) => return Ok(()),
                        Err(authorize_error) => {
                            let auth_error = rpc_error_summary(&auth);
                            return Err(format!(
                                "Discord rejected the OAuth token ({auth_error}), refresh failed: {}, and authorize failed: {}",
                                redact_secret_text(&refresh_error),
                                redact_secret_text(&authorize_error),
                            ));
                        }
                    }
                }
            }
        }
        Ok(())
    }

    fn reconnect_and_handshake(&mut self, client_id: &str) -> Result<(), String> {
        self.stream = open_first_pipe()?;
        let handshake = json!({ "v": 1, "client_id": client_id });
        self.write_frame(OpCode::Handshake, &handshake)?;
        let _ = self.read_frame()?;
        Ok(())
    }

    fn authorize_exchange_and_authenticate(
        &mut self,
        config: &DiscordConfig,
    ) -> Result<(), String> {
        let authorize = self.send_command(
            "AUTHORIZE",
            json!({
                "client_id": config.client_id,
                "scopes": DISCORD_RPC_SCOPES,
            }),
        )?;
        if rpc_has_error(&authorize) {
            return Err(format!(
                "Discord RPC AUTHORIZE failed: {}",
                rpc_error_summary(&authorize)
            ));
        }
        let code = authorize
            .get("data")
            .and_then(|data| data.get("code"))
            .and_then(Value::as_str)
            .ok_or_else(|| {
                "Discord RPC AUTHORIZE did not return an authorization code.".to_string()
            })?;
        let tokens = exchange_authorization_code(config, code)?;
        let retry = self.send_command(
            "AUTHENTICATE",
            json!({ "access_token": tokens.access_token }),
        )?;
        if rpc_has_error(&retry) {
            return Err("Discord rejected the OAuth token from AUTHORIZE.".into());
        }
        Ok(())
    }

    fn send_command(&mut self, command: &str, args: Value) -> Result<Value, String> {
        let nonce = make_nonce();
        let payload = json!({
            "cmd": command,
            "args": args,
            "nonce": nonce,
        });
        self.write_frame(OpCode::Frame, &payload)?;
        for _ in 0..10 {
            let response = self.read_frame()?;
            let response_nonce = response.get("nonce").and_then(Value::as_str);
            if response_nonce == Some(nonce.as_str()) || response_nonce.is_none() {
                return Ok(response);
            }
        }
        Err(format!(
            "Discord RPC did not return a response for {command}."
        ))
    }

    fn write_frame(&mut self, opcode: OpCode, payload: &Value) -> Result<(), String> {
        let bytes = serde_json::to_vec(payload).map_err(|e| e.to_string())?;
        self.stream
            .write_all(&encode_frame(opcode, &bytes))
            .map_err(|e| e.to_string())?;
        self.stream.flush().map_err(|e| e.to_string())
    }

    fn read_frame(&mut self) -> Result<Value, String> {
        let mut header = [0_u8; 8];
        self.stream
            .read_exact(&mut header)
            .map_err(|e| e.to_string())?;
        let (_op, len) = decode_frame_header(&header)?;
        if len > 10_000_000 {
            return Err("Discord IPC frame is too large.".into());
        }
        let mut body = vec![0_u8; len as usize];
        self.stream
            .read_exact(&mut body)
            .map_err(|e| e.to_string())?;
        serde_json::from_slice(&body).map_err(|e| e.to_string())
    }
}

fn parse_params(params: &str) -> Value {
    if params.trim().is_empty() || params.trim() == "{}" {
        return json!({});
    }
    serde_json::from_str(params).unwrap_or_else(|_| json!({ "raw": params }))
}

fn get_string(value: &Value, key: &str) -> String {
    value
        .get(key)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .trim()
        .to_string()
}

fn error(code: impl Into<String>, message: impl Into<String>) -> Value {
    json!({
        "status": "error",
        "error": code.into(),
        "message": message.into(),
    })
}

fn status_missing(
    config_error: Option<&String>,
    token_error: Option<&String>,
    pipe_available: bool,
) -> Vec<String> {
    let mut missing = Vec::new();
    if config_error.is_some() {
        missing.push("discord_config".to_string());
    }
    if token_error.is_some() {
        missing.push("discord_tokens".to_string());
    }
    if !pipe_available {
        missing.push("discord_ipc_pipe".to_string());
    }
    missing
}

fn load_config() -> Result<DiscordConfig, String> {
    let path = std::env::var("AEGIS_DISCORD_ENV_PATH").unwrap_or_else(|_| DEFAULT_ENV_PATH.into());
    let env = parse_env_file(Path::new(&path))?;
    let client_id = env
        .get("DISCORD_CLIENT_ID")
        .cloned()
        .ok_or_else(|| "DISCORD_CLIENT_ID is missing.".to_string())?;
    Ok(DiscordConfig {
        client_id,
        client_secret: env.get("DISCORD_CLIENT_SECRET").cloned(),
        token_endpoint: TOKEN_ENDPOINT.into(),
    })
}

fn load_tokens() -> Result<TokenFile, String> {
    let path = token_path();
    let raw =
        fs::read_to_string(&path).map_err(|e| format!("Could not read Discord token file: {e}"))?;
    serde_json::from_str(&raw).map_err(|e| format!("Could not parse Discord token file: {e}"))
}

fn token_path() -> PathBuf {
    std::env::var("AEGIS_DISCORD_TOKENS_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from(DEFAULT_TOKENS_PATH))
}

fn parse_env_file(path: &Path) -> Result<HashMap<String, String>, String> {
    let raw =
        fs::read_to_string(path).map_err(|e| format!("Could not read Discord env file: {e}"))?;
    let mut values = HashMap::new();
    for line in raw.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        if let Some((key, value)) = trimmed.split_once('=') {
            values.insert(key.trim().to_string(), strip_quotes(value.trim()));
        }
    }
    Ok(values)
}

fn strip_quotes(value: &str) -> String {
    let bytes = value.as_bytes();
    if bytes.len() >= 2
        && ((bytes[0] == b'"' && bytes[bytes.len() - 1] == b'"')
            || (bytes[0] == b'\'' && bytes[bytes.len() - 1] == b'\''))
    {
        value[1..value.len() - 1].to_string()
    } else {
        value.to_string()
    }
}

fn refresh_tokens(config: &DiscordConfig, tokens: &TokenFile) -> Result<TokenFile, String> {
    let refresh_token = tokens
        .refresh_token
        .as_deref()
        .filter(|s| !s.is_empty())
        .ok_or_else(|| "refresh_token is missing.".to_string())?;
    let mut form = vec![
        ("client_id", config.client_id.as_str()),
        ("grant_type", "refresh_token"),
        ("refresh_token", refresh_token),
    ];
    if let Some(client_secret) = config.client_secret.as_deref().filter(|s| !s.is_empty()) {
        form.push(("client_secret", client_secret));
    }

    let client = reqwest::blocking::Client::new();
    let response = client
        .post(&config.token_endpoint)
        .form(&form)
        .send()
        .map_err(|e| format!("Discord token refresh request failed: {e}"))?;
    if !response.status().is_success() {
        return Err(format!(
            "Discord token refresh failed with HTTP {}.",
            response.status()
        ));
    }
    let refreshed: TokenFile = response
        .json()
        .map_err(|e| format!("Discord token refresh response was invalid: {e}"))?;
    write_tokens_atomically(&refreshed)?;
    Ok(refreshed)
}

fn exchange_authorization_code(config: &DiscordConfig, code: &str) -> Result<TokenFile, String> {
    let mut form = vec![
        ("client_id", config.client_id.as_str()),
        ("grant_type", "authorization_code"),
        ("code", code),
        ("redirect_uri", REDIRECT_URI),
    ];
    if let Some(client_secret) = config.client_secret.as_deref().filter(|s| !s.is_empty()) {
        form.push(("client_secret", client_secret));
    }
    let client = reqwest::blocking::Client::new();
    let response = client
        .post(&config.token_endpoint)
        .form(&form)
        .send()
        .map_err(|e| format!("Discord authorization code exchange request failed: {e}"))?;
    if !response.status().is_success() {
        return Err(format!(
            "Discord authorization code exchange failed with HTTP {}.",
            response.status()
        ));
    }
    let tokens: TokenFile = response
        .json()
        .map_err(|e| format!("Discord authorization code exchange response was invalid: {e}"))?;
    write_tokens_atomically(&tokens)?;
    Ok(tokens)
}

fn write_tokens_atomically(tokens: &TokenFile) -> Result<(), String> {
    let path = token_path();
    let tmp = path.with_extension("json.tmp");
    let body = serde_json::to_string_pretty(tokens).map_err(|e| e.to_string())?;
    fs::write(&tmp, body)
        .map_err(|e| format!("Could not write refreshed Discord token file: {e}"))?;
    fs::rename(&tmp, &path)
        .map_err(|e| format!("Could not replace refreshed Discord token file: {e}"))
}

fn make_nonce() -> String {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    format!("aegis-{now}")
}

fn rpc_has_error(value: &Value) -> bool {
    value.get("evt").and_then(Value::as_str) == Some("ERROR")
        || value
            .get("data")
            .and_then(|d| d.get("code"))
            .is_some_and(Value::is_number)
}

fn rpc_error_summary(value: &Value) -> String {
    let data = value.get("data").unwrap_or(value);
    let code = data
        .get("code")
        .and_then(Value::as_i64)
        .map(|v| v.to_string());
    let message = data
        .get("message")
        .or_else(|| data.get("name"))
        .and_then(Value::as_str)
        .unwrap_or("unknown error");
    let mut summary = match code {
        Some(code) => format!("code {code}: {message}"),
        None => message.to_string(),
    };
    if message == "unknown error" {
        let mut sanitized = value.clone();
        redact_value(&mut sanitized);
        if let Ok(raw) = serde_json::to_string(&sanitized) {
            summary = format!(
                "unknown error payload: {}",
                raw.chars().take(500).collect::<String>()
            );
        }
    }
    redact_secret_text(&summary)
}

fn redact_secret_text(value: &str) -> String {
    let mut text = value.to_string();
    if let Ok(tokens) = load_tokens() {
        if !tokens.access_token.is_empty() {
            text = text.replace(&tokens.access_token, "[REDACTED]");
        }
        if let Some(refresh_token) = tokens.refresh_token.filter(|s| !s.is_empty()) {
            text = text.replace(&refresh_token, "[REDACTED]");
        }
    }
    if let Some((prefix, _)) = text.split_once("Invalid access token:") {
        return format!("{prefix}Invalid access token: [REDACTED]");
    }
    text
}

fn sanitize_rpc_result(value: Value) -> Value {
    let mut value = value;
    redact_value(&mut value);
    value
}

fn redact_value(value: &mut Value) {
    match value {
        Value::Object(map) => {
            for (key, child) in map.iter_mut() {
                if key.to_ascii_lowercase().contains("token")
                    || key.to_ascii_lowercase().contains("secret")
                {
                    *child = Value::String("[REDACTED]".into());
                } else {
                    redact_value(child);
                }
            }
        }
        Value::Array(items) => {
            for child in items {
                redact_value(child);
            }
        }
        _ => {}
    }
}

fn guilds_from_rpc_response(value: &Value) -> Result<Vec<GuildCandidate>, Value> {
    let data = value.get("data").unwrap_or(value);
    let guild_values = data
        .get("guilds")
        .or_else(|| data.get("items"))
        .and_then(Value::as_array)
        .ok_or_else(|| {
            error(
                "discord_rpc_shape_error",
                "GET_GUILDS response did not include guilds.",
            )
        })?;
    let mut guilds = Vec::new();
    for guild in guild_values {
        if let (Some(id), Some(name)) = (
            guild.get("id").and_then(Value::as_str),
            guild.get("name").and_then(Value::as_str),
        ) {
            guilds.push(GuildCandidate {
                id: id.into(),
                name: name.into(),
                channels: channels_from_guild(guild),
            });
        }
    }
    Ok(guilds)
}

fn channels_from_guild(value: &Value) -> Vec<ChannelCandidate> {
    let data = value.get("data").unwrap_or(value);
    data.get("channels")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|channel| {
            let id = channel.get("id").and_then(Value::as_str)?;
            let name = channel.get("name").and_then(Value::as_str)?;
            let channel_type = channel.get("type").and_then(Value::as_i64).unwrap_or(-1);
            Some(ChannelCandidate {
                id: id.into(),
                name: name.into(),
                channel_type,
            })
        })
        .collect()
}

fn is_voice_channel(channel_type: i64) -> bool {
    channel_type == 2 || channel_type == 13
}

fn normalized_contains(haystack: &str, needle: &str) -> bool {
    let h = normalize_name(haystack);
    let n = normalize_name(needle);
    !n.is_empty() && (h == n || h.contains(&n))
}

fn normalize_name(value: &str) -> String {
    value
        .chars()
        .filter(|c| !c.is_whitespace() && *c != '-' && *c != '_' && *c != '　')
        .flat_map(char::to_lowercase)
        .collect()
}

fn find_pipe_path() -> Option<String> {
    (0..10)
        .map(|i| format!(r"\\.\pipe\discord-ipc-{i}"))
        .find(|path| pipe_exists(path))
}

fn open_first_pipe() -> Result<Box<dyn ReadWrite>, String> {
    for i in 0..10 {
        let path = format!(r"\\.\pipe\discord-ipc-{i}");
        if let Ok(stream) = open_pipe(&path) {
            return Ok(stream);
        }
    }
    Err("Discord IPC pipe was not found. Is Discord running?".into())
}

#[cfg(target_os = "windows")]
fn pipe_exists(path: &str) -> bool {
    std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .open(path)
        .is_ok()
}

#[cfg(not(target_os = "windows"))]
fn pipe_exists(_path: &str) -> bool {
    false
}

#[cfg(target_os = "windows")]
fn open_pipe(path: &str) -> Result<Box<dyn ReadWrite>, String> {
    std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .open(path)
        .map(|f| Box::new(f) as Box<dyn ReadWrite>)
        .map_err(|e| format!("Could not open Discord IPC pipe: {e}"))
}

#[cfg(not(target_os = "windows"))]
fn open_pipe(_path: &str) -> Result<Box<dyn ReadWrite>, String> {
    Err("Discord IPC over named pipes is only supported on Windows in pc-server.".into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frame_codec_uses_little_endian_header() {
        let frame = encode_frame(OpCode::Frame, br#"{"cmd":"PING"}"#);
        assert_eq!(&frame[0..4], &1_u32.to_le_bytes());
        assert_eq!(&frame[4..8], &14_u32.to_le_bytes());
        assert_eq!(&frame[8..], br#"{"cmd":"PING"}"#);
        assert_eq!(decode_frame_header(&frame[0..8]).unwrap(), (1, 14));
    }

    #[test]
    fn resolver_matches_exact_guild_and_first_voice_channel() {
        let guilds = vec![GuildCandidate {
            id: "g1".into(),
            name: "memo".into(),
            channels: vec![
                ChannelCandidate {
                    id: "t1".into(),
                    name: "text".into(),
                    channel_type: 0,
                },
                ChannelCandidate {
                    id: "v1".into(),
                    name: "通話".into(),
                    channel_type: 2,
                },
            ],
        }];

        let (_guild, channel) = resolve_voice_channel(&guilds, "memo", None).unwrap();
        assert_eq!(channel.id, "v1");
    }

    #[test]
    fn resolver_reports_ambiguous_guilds() {
        let guilds = vec![
            GuildCandidate {
                id: "g1".into(),
                name: "memo".into(),
                channels: vec![],
            },
            GuildCandidate {
                id: "g2".into(),
                name: "memo 2".into(),
                channels: vec![],
            },
        ];

        let err = resolve_voice_channel(&guilds, "memo", None).unwrap_err();
        assert_eq!(err["status"], "ambiguous");
    }

    #[test]
    fn sanitize_redacts_token_and_secret_fields() {
        let result = sanitize_rpc_result(json!({
            "access_token": "abc",
            "nested": {"client_secret": "def", "ok": true}
        }));
        assert_eq!(result["access_token"], "[REDACTED]");
        assert_eq!(result["nested"]["client_secret"], "[REDACTED]");
        assert_eq!(result["nested"]["ok"], true);
    }
}
