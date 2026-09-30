"""Local text-to-speech — the engine that needs no egress at all.

**Why this exists.** ``TextToSpeechService`` had exactly one engine, ``edge-tts``, which is
a *cloud* service: it sends the text to Microsoft. So the constraint refused it by default,
and the refusal message told the operator to "configure a local TTS provider instead" —
naming a provider that did not exist anywhere in the repository. ``VoiceSettings`` lists
``os-tts`` and ``piper`` as options; neither was implemented. A refusal that recommends an
unavailable alternative is not a safety control, it is a dead end.

This module supplies the ``os-tts`` option for real: it drives the speech engine the
operating system already ships. Nothing here opens a socket, so the local path needs no
egress permission and cannot be broken by one.

Engines, in order of preference
-------------------------------
* **Windows** — SAPI via ``System.Speech.Synthesis.SpeechSynthesizer``, driven through
  PowerShell with ``SetOutputToWaveFile``, so the output is a file like every other
  provider's.
* **macOS** — ``say``, which writes an audio file with ``-o``.
* **Linux** — ``espeak-ng`` (or ``espeak``) with ``-w``.

The text is handed over through a **UTF-8 temp file**, never as a command-line argument.
Voice text is user content and is frequently non-ASCII; passing it as an argument would
make the result depend on the console code page and on shell quoting, which is how a
"local" path silently mangles the very text it is meant to speak. Paths stay ASCII by
construction (``tempfile``), so only the *content* needs the file.

An unavailable engine is reported, never faked
----------------------------------------------
If no engine is present the result says so and names what to install. Returning a
zero-length "success" would be the worst outcome: the caller would believe the user had
been spoken to.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

logger = logging.getLogger("aegis_ai.integrations.local_tts")

#: How long a single synthesis may take. Generous — a long passage read at speech rate is
#: slow — but bounded, so a wedged engine cannot hang a request forever.
_TIMEOUT_SECONDS = 120


def available_engine() -> str:
    """The local engine this machine can drive, or ``""`` when there is none.

    Reported rather than assumed: the answer differs per machine, and a caller that cannot
    synthesise should say so instead of failing obscurely later.
    """
    if sys.platform.startswith("win"):
        return "sapi" if shutil.which("powershell") or shutil.which("pwsh") else ""
    if sys.platform == "darwin":
        return "say" if shutil.which("say") else ""
    for candidate in ("espeak-ng", "espeak"):
        if shutil.which(candidate):
            return candidate
    return ""


def _powershell() -> str:
    return shutil.which("powershell") or shutil.which("pwsh") or ""


def _powershell_literal(value: str) -> str:
    """A single-quoted PowerShell string literal.

    Single quotes make every other character literal; the only escape needed is ``'``
    itself, which doubles. Interpolation is off inside single quotes, so a ``$`` in a path
    cannot become a variable reference.
    """
    return "'" + str(value).replace("'", "''") + "'"


def _run(command: list[str], *, text_file: Path | None = None) -> tuple[bool, str]:
    """Run an engine. Returns ``(ok, error)``; never raises."""
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"the local speech engine did not finish within {_TIMEOUT_SECONDS}s"
    except OSError as exc:
        return False, f"could not start the local speech engine: {exc}"
    finally:
        if text_file is not None:
            try:
                text_file.unlink()
            except OSError:
                pass

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or b"").decode("utf-8", errors="replace")
        return False, f"the local speech engine exited {completed.returncode}: {detail.strip()[:300]}"
    return True, ""


def synthesize_to_file(*, text: str, output_path: str, rate_percent: int = 0) -> tuple[bool, str]:
    """Write ``text`` spoken aloud to ``output_path`` using the OS engine.

    Returns ``(ok, error)``. ``rate_percent`` is the engine's speaking-rate adjustment
    (negative is slower); it is ignored by engines that cannot express it, rather than
    being silently applied as something else.
    """
    engine = available_engine()
    if not engine:
        return False, (
            "no local speech engine is available: install one of "
            "Windows SAPI (built in), macOS `say`, or `espeak-ng` on Linux"
        )

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8", newline=""
    )
    text_file = Path(handle.name)
    try:
        handle.write(text)
        handle.close()
    except OSError as exc:
        handle.close()
        return False, f"could not stage the text for the local engine: {exc}"

    if engine == "sapi":
        # `-EncodedCommand` accepts **no** further arguments — PowerShell refuses the whole
        # invocation ("Cannot process the command because -Command or -EncodedCommand is
        # already specified", measured on Windows PowerShell 5.1). So the paths go *inside*
        # the script as literals. They are `tempfile`-generated and therefore ASCII, and
        # `_powershell_literal` escapes the one character that could still break out.
        rate = max(-10, min(10, rate_percent // 10))
        script = (
            "Add-Type -AssemblyName System.Speech\n"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
            f"$s.Rate = {rate}\n"
            f"$s.SetOutputToWaveFile({_powershell_literal(str(target))})\n"
            "$s.Speak([System.IO.File]::ReadAllText("
            f"{_powershell_literal(str(text_file))}, [System.Text.Encoding]::UTF8))\n"
            "$s.Dispose()\n"
        )
        # Only the *script* is encoded (and it is ASCII), so non-ASCII voice text travels
        # through the UTF-8 file rather than through any command line. The script is never
        # written to disk.
        import base64

        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        command = [_powershell(), "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded]
        return _run(command, text_file=text_file)

    if engine == "say":
        command = ["say", "-f", str(text_file), "-o", str(target)]
        if rate_percent:
            command += ["-r", str(max(80, 200 + (200 * rate_percent // 100)))]
        return _run(command, text_file=text_file)

    # espeak-ng / espeak
    command = [engine, "-f", str(text_file), "-w", str(target)]
    if rate_percent:
        command += ["-s", str(max(80, 175 + (175 * rate_percent // 100)))]
    return _run(command, text_file=text_file)


def probe(*, text: str = "aegis voice check") -> tuple[bool, str]:
    """Synthesise a short phrase into a temp file, to prove the engine really works.

    A named engine in ``PATH`` is not proof that synthesis succeeds — the Linux engines in
    particular can be installed without a usable voice data file. This exercises the whole
    path and cleans up after itself.
    """
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "probe.wav"
        ok, error = synthesize_to_file(text=text, output_path=str(target))
        if not ok:
            return False, error
        if not target.exists() or target.stat().st_size == 0:
            return False, "the local speech engine reported success but wrote no audio"
        return True, f"{available_engine()} wrote {target.stat().st_size} bytes"


def duration_ms(started_at: float) -> float:
    """Elapsed milliseconds — kept here so callers time the engine the same way."""
    return (time.perf_counter() - started_at) * 1000.0
