from __future__ import annotations


class KitError(Exception):
    """A problem the person can fix. The CLI prints the message and the hint, never a traceback."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint
