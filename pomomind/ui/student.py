"""Student area: Pomodoro timer with ambient sound, and the course feed."""
import time

import streamlit as st

from pomomind import state
from pomomind.config import POMODORO_SECONDS, SOUNDS, XP_FLASHCARDS, XP_POMODORO
from pomomind.i18n import t
from pomomind.models import ApiSettings
from pomomind.services import gemini
from pomomind.services.course_store import course_store


def render(api: ApiSettings) -> None:
    st.title(t("student.title"))

    course = course_store.current()
    if course:
        st.info(t("student.notification", subject=course.subject, filename=course.filename))

    timer_tab, feed_tab = st.tabs([t("student.tab_timer"), t("student.tab_feed")])
    with timer_tab:
        _timer_tab()
    with feed_tab:
        _feed_tab(api)


def _timer_tab() -> None:
    st.subheader(t("timer.subheader"))

    sound = st.selectbox(t("timer.sound"), list(SOUNDS), format_func=lambda k: t(f"sound.{k}"))
    if SOUNDS[sound]:
        st.audio(SOUNDS[sound], format="audio/mp3", start_time=0)

    if st.button(t("timer.start")):
        display = st.empty()
        for remaining in range(POMODORO_SECONDS, 0, -1):
            display.metric(t("timer.focus"), f"00:{remaining:02d}")
            time.sleep(1)
        st.balloons()
        state.add_xp(XP_POMODORO)
        st.success(t("timer.done"))
        st.rerun()  # refresh the XP metric in the sidebar


def _feed_tab(api: ApiSettings) -> None:
    st.subheader(t("feed.subheader"))

    course = course_store.current()
    if course is None:
        st.write(t("feed.empty"))
        return

    st.write(t("feed.document", filename=course.filename, subject=course.subject))

    if st.button(t("feed.flashcards_button")):
        if not api.ready:
            st.error(t("feed.missing_key"))
        else:
            with st.spinner(t("feed.spinner")):
                try:
                    text = gemini.generate_flashcards(api, course)
                except Exception as err:
                    st.error(t("feed.error", error=err))
                else:
                    st.session_state.flashcards = (course.filename, text)
                    state.add_xp(XP_FLASHCARDS)
                    st.toast(t("feed.success"))
                    st.rerun()  # refresh the XP metric in the sidebar

    saved = st.session_state.flashcards
    if saved and saved[0] == course.filename:
        st.markdown("---")
        st.write(saved[1])
