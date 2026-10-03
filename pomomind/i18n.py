"""Translation helper. Usage: t("login.title") or t("sidebar.title", role="Student")."""
import streamlit as st

from pomomind.config import DEFAULT_LANGUAGE
from pomomind.locales import STRINGS

LANGUAGE_KEY = "language"  # st.session_state key set by the sidebar selector


def current_language() -> str:
    return st.session_state.get(LANGUAGE_KEY, DEFAULT_LANGUAGE)


def t(key: str, **values) -> str:
    text = STRINGS[current_language()][key]
    return text.format(**values) if values else text
