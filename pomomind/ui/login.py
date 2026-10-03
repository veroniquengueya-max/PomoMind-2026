"""Login screen."""
import streamlit as st

from pomomind import state
from pomomind.auth import authenticate
from pomomind.config import ROLES
from pomomind.i18n import t


def render() -> None:
    st.title(t("login.title"))
    st.subheader(t("login.subtitle"))

    role = st.radio(t("login.role"), ROLES, format_func=lambda r : t(f"role.{r}"))
    username = st.text_input(t("login.username"), placeholder="student, prof_bio, prof_cyber")
    password = st.text_input(t("login.password"), type="password")

    if st.button(t("login.button")):
        user = authenticate(username, password, role)
        if user:
            state.log_in(user)
            st.success(t("login.welcome"))
            st.rerun()
        else:
            st.error(t("login.error"))
