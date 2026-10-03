"""Professor dashboard: upload a course PDF, have the AI verify it, broadcast it."""
import time

import streamlit as st

from pomomind.config import BROADCAST_COOLDOWN_SECONDS
from pomomind.i18n import t
from pomomind.models import ApiSettings, Course
from pomomind.services import gemini
from pomomind.services.course_store import course_store


def render(api: ApiSettings) -> None:
    subject = st.session_state.subject
    st.title(t("professor.title", subject=subject))
    st.write(t("professor.intro"))

    uploaded_pdf = st.file_uploader(t("professor.uploader"), type=["pdf"])

    if st.button(t("professor.broadcast")):
        _broadcast(api, subject, uploaded_pdf)


def _broadcast(api: ApiSettings, subject: str, uploaded_pdf) -> None:
    now = time.time()
    if now - st.session_state.last_broadcast_ts < BROADCAST_COOLDOWN_SECONDS:
        st.warning(t("professor.spam"))
    elif not api.ready:
        st.error(t("professor.missing_key"))
    elif uploaded_pdf is None:
        st.warning(t("professor.missing_pdf"))
    else:
        with st.spinner(t("professor.spinner")):
            try:
                pdf_bytes = uploaded_pdf.getvalue()
                verdict = gemini.verify_course(api, subject, pdf_bytes)
                if verdict.approved:
                    course_store.publish(Course(uploaded_pdf.name, subject, pdf_bytes))
                    st.session_state.last_broadcast_ts = now
                    st.success(t("professor.success", subject=subject))
                else:
                    st.error(t("professor.blocked", reason=verdict.message))
            except Exception as err:
                st.error(t("professor.error", error=err))
