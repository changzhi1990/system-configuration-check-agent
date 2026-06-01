from __future__ import annotations

import shlex
import subprocess
import time
from pathlib import Path

from core.models import CommandExecution


class CommandRunner:
    def __init__(self, default_timeout: int = 15) -> None:
        self.default_timeout = default_timeout

    def run(self, command: list[str], timeout: int | None = None) -> CommandExecution:
        started = time.perf_counter()
        timeout = timeout or self.default_timeout
        display = " ".join(shlex.quote(part) for part in command)
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return CommandExecution(
                command=display,
                args=command,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
                returncode=completed.returncode,
                timed_out=False,
                command_found=True,
                duration_seconds=round(time.perf_counter() - started, 4),
            )
        except FileNotFoundError:
            return CommandExecution(
                command=display,
                args=command,
                stdout="",
                stderr=f"command not found: {command[0]}",
                returncode=127,
                timed_out=False,
                command_found=False,
                duration_seconds=round(time.perf_counter() - started, 4),
            )
        except subprocess.TimeoutExpired as exc:
            return CommandExecution(
                command=display,
                args=command,
                stdout=(exc.stdout or "").strip(),
                stderr=((exc.stderr or "") + f"\nTimed out after {timeout} seconds").strip(),
                returncode=124,
                timed_out=True,
                command_found=True,
                duration_seconds=round(time.perf_counter() - started, 4),
            )

    def read_text_file(self, path: str | Path) -> CommandExecution:
        file_path = Path(path)
        if not file_path.exists():
            return CommandExecution(
                command=f"read_file {file_path}",
                args=[str(file_path)],
                stdout="",
                stderr=f"file not found: {file_path}",
                returncode=2,
                timed_out=False,
                command_found=True,
                duration_seconds=0.0,
            )
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            return CommandExecution(
                command=f"read_file {file_path}",
                args=[str(file_path)],
                stdout=content.strip(),
                stderr="",
                returncode=0,
                timed_out=False,
                command_found=True,
                duration_seconds=0.0,
            )
        except PermissionError:
            return CommandExecution(
                command=f"read_file {file_path}",
                args=[str(file_path)],
                stdout="",
                stderr=f"permission denied: {file_path}",
                returncode=13,
                timed_out=False,
                command_found=True,
                duration_seconds=0.0,
            )
