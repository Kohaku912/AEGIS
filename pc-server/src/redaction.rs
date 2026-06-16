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

/// Check if a path is in a sensitive directory that should not be monitored.
pub fn is_sensitive_directory(path: &str) -> bool {
    let sensitive_patterns = [
        ".ssh",
        ".gnupg",
        ".aws",
        ".gcloud",
        ".azure",
        "AppData\\Roaming\\Microsoft\\Crypto",
        "/etc/ssl",
        "/etc/ssh",
    ];
    let path_lower = path.to_lowercase();
    sensitive_patterns
        .iter()
        .any(|p| path_lower.contains(&p.to_lowercase()))
}

/// Check if a path contains credential files that should be excluded.
pub fn is_credential_file(path: &str) -> bool {
    let cred_patterns = [
        ".pem",
        ".key",
        ".crt",
        "credentials",
        ".env",
        "id_rsa",
        "id_ed25519",
        "token",
        "secret",
        "password",
    ];
    let path_lower = path.to_lowercase();
    cred_patterns.iter().any(|p| path_lower.contains(p))
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
}
