"""Base adapter interface for ChatGPT Visible Bridge."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..schema import Result, Task


class Adapter(ABC):
    """Base adapter for sending prompts to ChatGPT and receiving responses."""

    name: str = "base"

    @abstractmethod
    def send(self, task: Task) -> Result:
        """Process a task and return a result."""
        ...

    @property
    def available(self) -> bool:
        """Return whether this adapter is ready to use."""
        return True
