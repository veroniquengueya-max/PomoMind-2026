"""PomoMind AI - Streamlit entry point.

Run with:  streamlit run app.py

This file only wires things together. Features live in the `pomomind` package.
"""
import streamlit as st

from pomomind import state
from pomomind.config import APP_ICON, APP_NAME, ROLE_PROFESSOR
from pomomind.ui import login, professor, sidebar, student

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON)

state.init()
sidebar.language_selector()

if not state.is_logged_in():
    login.render()
else:
    api = sidebar.account_panel()
    if st.session_state.role == ROLE_PROFESSOR:
        professor.render(api)
    else:
        student.render(api)
