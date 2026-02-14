"""Shared mutable search progress state consumed by the UI."""

class SearchProgress:
    def __init__(self) -> None:
        self.result_count = 0
        self.progress_percent = 0.0
        self.error_message: str | None = None
