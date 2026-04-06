"""Per-session conversation memory manager."""
from langchain.memory import ConversationBufferWindowMemory

from app.config import get_settings

_sessions: dict[str, ConversationBufferWindowMemory] = {}


def get_memory(session_id: str) -> ConversationBufferWindowMemory:
    """Return (or create) a windowed conversation memory for a session."""
    if session_id not in _sessions:
        settings = get_settings()
        _sessions[session_id] = ConversationBufferWindowMemory(
            k=settings.memory_window,
            return_messages=True,
            memory_key="chat_history",
            input_key="question",
            output_key="answer",
        )
    return _sessions[session_id]


def clear_memory(session_id: str) -> None:
    """Clear conversation history for a session."""
    if session_id in _sessions:
        _sessions[session_id].clear()
        del _sessions[session_id]


def list_sessions() -> list[str]:
    """Return all active session IDs."""
    return list(_sessions.keys())
