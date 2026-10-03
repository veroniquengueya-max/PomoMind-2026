"""Sidebar: language picker (always) and account panel (logged-in only)."""
import streamlit as st

from pomomind import state
from pomomind.config import LANGUAGES, ROLE_STUDENT
from pomomind.i18n import LANGUAGE_KEY, t
from pomomind.models import ApiSettings


def language_selector() -> None:
    st.sidebar.selectbox(
        t("language.label"),
        list(LANGUAGES),
        format_func=lambda code : LANGUAGES[code],
    )


def account_panel() -> ApiSettings:
    """Render role info, API settings and logout. Returns the collected API settings."""
    role = st.session_state.role
    st.sidebar.title(t("sidebar.title", role=t(f"role.{role}")))

    if role == ROLE_STUDENT:
        st.sidebar.metric(t("sidebar.streak"), t("sidebar.streak_value"))
        st.sidebar.metric(t("sidebar.score"), f"{st.session_state.xp} XP")

    demo = st.sidebar.checkbox(t("sidebar.demo_mode"), value=False)
    key = "" if demo else st.sidebar.text_input(t("sidebar.api_key"), type="password")

    if st.sidebar.button(t("sidebar.logout")):
        state.log_out()
        st.rerun()

    return ApiSettings(demo=demo, key=key)
