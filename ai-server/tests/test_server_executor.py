from server_executor import ServerExecutor


class _Manifest:
    tcp_command = "read_file {path}|{max_bytes}"


def test_format_tcp_command_allows_missing_optional_args() -> None:
    cmd = ServerExecutor._format_tcp_command(
        "execute_powershell {command}|{working_dir}",
        {"command": "Get-Location"},
    )

    assert cmd == "execute_powershell Get-Location|"


def test_format_tcp_command_keeps_present_args_and_normalizes_bool() -> None:
    cmd = ServerExecutor._format_tcp_command(
        "list_files {path}|{recursive}",
        {"path": r"C:\Users", "recursive": False},
    )

    assert cmd == r"list_files C:\Users|false"


def test_pc_tcp_invalid_json_is_not_reported_as_unreachable(monkeypatch) -> None:
    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def settimeout(self, timeout):
            self.timeout = timeout

        def connect(self, address):
            self.address = address

        def sendall(self, data):
            self.data = data

        def recv(self, size):
            return (
                b'{"content":"Email: aegis@example.com\r\n'
                b"Password: secret123\r\n"
                b'Phone Number: 07084976713"}\n'
            )

    monkeypatch.setattr("server_executor.socket.socket", lambda: FakeSocket())

    result = ServerExecutor()._execute_pc_tcp(
        "pc-server.file.read",
        {"path": r"C:\Users\AEGIS\Desktop\google_account_info.txt", "max_bytes": 10000},
        _Manifest(),
    )

    assert "Invalid JSON from PC server" in result["error"]
    assert "PC server unreachable" not in result["error"]
    assert result["capability_id"] == "pc-server.file.read"
    assert "[EMAIL_REDACTED]" in result["raw_preview"]
    assert "secret123" not in result["raw_preview"]
    assert "07084976713" not in result["raw_preview"]
