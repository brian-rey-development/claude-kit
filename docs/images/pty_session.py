"""Runs a command in a pseudo terminal and answers its questions, the way a person at the keyboard would."""

from __future__ import annotations

import fcntl
import os
import pty
import re
import select
import struct
import subprocess
import termios
from collections.abc import Mapping, Sequence
from pathlib import Path

ESCAPES = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
TIMEOUT_SECONDS = 60
ROWS = 60


def _plain(output: bytes) -> str:
    return ESCAPES.sub("", output.decode(errors="ignore")).rstrip()


def _read(master: int) -> bytes:
    if not select.select([master], [], [], TIMEOUT_SECONDS)[0]:
        raise TimeoutError("The command stopped printing without finishing.")
    try:
        return os.read(master, 4096)
    except OSError:
        return b""


def run(
    argv: Sequence[str],
    *,
    columns: int,
    answers: Sequence[tuple[str, str]] = (),
    env: Mapping[str, str],
    cwd: Path,
) -> str:
    """The command's output, with each answer typed once the output ends with its prompt."""
    master, child = pty.openpty()
    fcntl.ioctl(child, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, columns, 0, 0))
    process = subprocess.Popen(argv, stdin=child, stdout=child, stderr=child, env=env, cwd=cwd)
    os.close(child)
    output, pending = b"", list(answers)
    while chunk := _read(master):
        output += chunk
        if pending and _plain(output).endswith(pending[0][0]):
            os.write(master, f"{pending.pop(0)[1]}\n".encode())
    os.close(master)
    process.wait()
    return output.decode().replace("\r\n", "\n")
