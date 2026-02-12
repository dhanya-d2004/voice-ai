from collections import deque
from typing import List, Tuple

class ShaktiMemory:
    """
    Simple rolling memory for conversation context.
    Stores (role, content) tuples.
    """

    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.buffer = deque(maxlen=max_turns)

    def add(self, role: str, content: str):
        if role not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        self.buffer.append((role, content))

    def get_recent(self) -> List[Tuple[str, str]]:
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()
