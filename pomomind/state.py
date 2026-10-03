"""Session-state helpers. Every key in st.session_state is declared here."""
import streamlit as st

from pomomind.config import STARTING_XP, ROLE_STUDENT
from pomomind.models import User

DEFAULTS = {
    "logged_in": False,
    "role": ROLE_STUDENT,
    "username": "",
    "subject": None,
    "xp": STARTING_XP,
    "last_broadcast_ts": 0.0,  # professor anti-spam timestamp
    "flashcards": None,        # (course filename, generated text)
}


def init() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def is_logged_in() -> bool:
    return st.session_state["logged_in"]


def log_in(user: User) -> None:
    st.session_state.update(
        {"logged_in": True, "role": user.role, "username": user.username, "subject": user.subject}
    )


def log_out() -> None:
    st.session_state.clear()


def add_xp(amount: int) -> None:
    st.session_state.xp += amount
