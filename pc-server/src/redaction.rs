//! Secret redaction for clipboard and log output.
//!
//! Detects and masks sensitive patterns:
//! - Passwords, tokens, API keys, secrets
//! - SSH keys, PEM data
//! - Authorization headers
//! - Connection strings with credentials

use regex::Regex;
use std::sync::LazyLock;

static REDACT_PATTERNS: LazyLock<Vec<(Regex, &str)>> = LazyLock::new(|| {
    vec![
        // Passwords in key=value or JSON
        (
            Regex::new(r#"(?i)(password|passwd|secret|token|api[_-]?key|apikey)\s*[=:]\s*["']?[^\s"',;}]+"#)
                .unwrap(),
            r#"$1=[REDACTED]"#,
        ),
        // Authorization headers
        (
            Regex::new(r"(?i)Authorization:\s*[^\n]+").unwrap(),
            "Authorization: [REDACTED]",
        ),
        // SSH private keys
        (
            Regex::new(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----[\s\S]*?-----END (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----").unwrap(),
            "[SSH_PRIVATE_KEY_REDACTED]",
        ),
        // PEM certificates
        (
            Regex::new(r"-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----").unwrap(),
            "[PEM_CERTIFICATE_REDACTED]",
        ),
        // JWT tokens (eyJ...)
        (
            Regex::new(r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*").unwrap(),
            "[JWT_REDACTED]",
        ),
        // AWS access keys (AKIA...)
        (
            Regex::new(r"AKIA[0-9A-Z]{16}").unwrap(),
            "[AWS_KEY_REDACTED]",
        ),
        // Connection strings with passwords
        (
            Regex::new(r#"(?i)(mongodb|postgres|mysql|redis)://[^:]*:[^@]*@"#).unwrap(),
            r#"$1://[USER]:[REDACTED]@"#,
        ),
    ]
});

/// Redact secrets from a text string.
/// Returns the redacted string (secrets replaced with [REDACTED]).
pub fn redact_secrets(text: &str) -> String {
    let mut result = text.to_string();
    for (pattern, replacement) in REDACT_PATTERNS.iter() {
        result = pattern.replace_all(&result, *replacement).to_string();
    }
    result
}

/// Split a path into lower-cased components, treating both separators.
///
/// Deliberately not `std::path`: the strings arriving from the AI Server may use
/// either separator regardless of the host OS.
fn path_components_lower(path: &str) -> Vec<String> {
    path.split(['/', '\\'])
        .filter(|component| !component.is_empty())
        .map(|component| component.to_lowercase())
        .collect()
}

fn file_name_lower(path: &str) -> String {
    path_components_lower(path).pop().unwrap_or_default()
}

/// Directory *components* that mark a path as sensitive.
///
/// Matched as whole components, so `C:\Users\me\.ssh` and `/home/me/.ssh/known_hosts`
/// match while `notes-about-.sshrc.md` does not.
const SENSITIVE_DIR_COMPONENTS: [&str; 5] = [".ssh", ".gnupg", ".aws", ".gcloud", ".azure"];

/// Multi-segment fragments that cannot be matched component-wise.
const SENSITIVE_DIR_FRAGMENTS: [&str; 3] = [
    "appdata\\roaming\\microsoft\\crypto",
    "/etc/ssl",
    "/etc/ssh",
];

/// Check if a path is inside a sensitive directory.
pub fn is_sensitive_directory(path: &str) -> bool {
    if path_components_lower(path)
        .iter()
        .any(|component| SENSITIVE_DIR_COMPONENTS.contains(&component.as_str()))
    {
        return true;
    }
    let lower = path.to_lowercase();
    SENSITIVE_DIR_FRAGMENTS
        .iter()
        .any(|fragment| lower.contains(fragment))
}

/// Well-known credential file names, matched exactly.
const CREDENTIAL_FILE_NAMES: [&str; 9] = [
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".netrc", ".pgpass", ".npmrc", ".pypirc",
    ".htpasswd",
];

/// Extensions that denote key material.
const CREDENTIAL_EXTENSIONS: [&str; 8] = [
    ".pem", ".key", ".crt", ".p12", ".pfx", ".jks", ".keystore", ".ppk",
];

/// Words that mark a file name as credential-bearing when they appear as a whole
/// `-`/`_`/`.`-separated part.
///
/// Token-boundary matching is what keeps this precise: `token.json` and
/// `access_token` match, while `tokenizer.py` and `secretary.py` do not.
const CREDENTIAL_WORDS: [&str; 12] = [
    "credential", "credentials", "creds", "secret", "secrets", "password", "passwd", "token",
    "tokens", "apikey", "auth", "private_key",
];

/// Suffixes that mark a file as a non-secret template.
const TEMPLATE_SUFFIXES: [&str; 4] = [".example", ".template", ".sample", ".dist"];

/// Check if a path points at a credential-bearing file.
pub fn is_credential_file(path: &str) -> bool {
    let name = file_name_lower(path);
    if name.is_empty() {
        return false;
    }
    // `.env.example` and friends document the shape of a secret, not the secret.
    if TEMPLATE_SUFFIXES
        .iter()
        .any(|suffix| name.ends_with(suffix))
    {
        return false;
    }
    if name == ".env" || name.starts_with(".env.") {
        return true;
    }
    if CREDENTIAL_FILE_NAMES.contains(&name.as_str()) {
        return true;
    }
    if CREDENTIAL_EXTENSIONS
        .iter()
        .any(|extension| name.ends_with(extension))
    {
        return true;
    }
    name.split(['-', '_', '.'])
        .any(|part| CREDENTIAL_WORDS.contains(&part))
}

/// Paths AEGIS must not read, write, delete, copy from, or move from.
///
/// Single entry point for enforcement. `is_sensitive_directory` and
/// `is_credential_file` are the definition; every mutating or reading file
/// operation in this crate must consult this function rather than re-deriving
/// its own classification.
pub fn is_protected_path(path: &str) -> bool {
    is_sensitive_directory(path) || is_credential_file(path)
}

/// Standard rejection message for a protected path.
pub fn protected_path_error(operation: &str, path: &str) -> String {
    format!("Refusing to {operation} a protected path: {path}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_redact_password() {
        let input = r#"password=mysecret123 user=alice"#;
        let result = redact_secrets(input);
        assert!(result.contains("[REDACTED]"));
        assert!(!result.contains("mysecret123"));
    }

    #[test]
    fn test_redact_token() {
        let input = r#"token=abc123xyz args"#;
        let result = redact_secrets(input);
        assert!(result.contains("[REDACTED]"));
        assert!(!result.contains("abc123xyz"));
    }

    #[test]
    fn test_safe_values_preserved() {
        let input = r#"path="/tmp/file.txt" user="alice""#;
        let result = redact_secrets(input);
        assert!(result.contains("/tmp/file.txt"));
        assert!(result.contains("alice"));
    }

    #[test]
    fn test_sensitive_directory() {
        assert!(is_sensitive_directory("/home/user/.ssh"));
        assert!(is_sensitive_directory("C:\\Users\\user\\.aws"));
        assert!(!is_sensitive_directory("/home/user/Documents"));
    }

    #[test]
    fn test_credential_file() {
        assert!(is_credential_file("id_rsa"));
        assert!(is_credential_file("config/credentials.yml"));
        assert!(!is_credential_file("readme.md"));
    }

    #[test]
    fn test_credential_words_match_on_token_boundaries_only() {
        // Real secrets.
        assert!(is_credential_file("token.json"));
        assert!(is_credential_file("access_token"));
        assert!(is_credential_file("refresh-token.txt"));
        assert!(is_credential_file("my_secret_notes.txt"));
        assert!(is_credential_file("auth.json"));
        // Not secrets — the substring alone must not match.
        assert!(!is_credential_file("tokenizer.py"));
        assert!(!is_credential_file("secretary.py"));
        assert!(!is_credential_file("authored_notes.md"));
        assert!(!is_credential_file("passwords_test_plan.md"));
    }

    #[test]
    fn test_templates_are_not_credentials() {
        assert!(is_credential_file(".env"));
        assert!(is_credential_file(".env.local"));
        assert!(!is_credential_file(".env.example"));
        assert!(!is_credential_file("credentials.sample"));
    }

    #[test]
    fn test_sensitive_directory_matches_whole_components() {
        assert!(is_sensitive_directory("C:\\Users\\me\\.ssh"));
        assert!(is_sensitive_directory("/home/me/.ssh/known_hosts"));
        assert!(is_sensitive_directory("/home/me/.gnupg/secring.gpg"));
        assert!(is_sensitive_directory("/etc/ssl/private/server.pem"));
        // The marker must be a directory component, not a substring.
        assert!(!is_sensitive_directory("/home/me/notes-about-.sshrc.md"));
        assert!(!is_sensitive_directory("/home/me/aws-notes/report.md"));
    }

    #[test]
    fn test_is_protected_path_covers_both_predicates() {
        assert!(is_protected_path("/home/me/.ssh/id_rsa"));
        assert!(is_protected_path("C:\\Users\\me\\Documents\\token.json"));
        assert!(!is_protected_path("/home/me/Documents/report.md"));
        assert!(!is_protected_path("C:\\Users\\me\\programs\\AEGIS\\AGENTS.md"));
    }
}
