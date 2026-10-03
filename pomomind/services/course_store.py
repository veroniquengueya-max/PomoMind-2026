"""Shared store for the currently broadcast course.

st.session_state is per browser session, so it cannot carry a course from a
professor to students. This module-level singleton is shared by every session
in the same server process, which is enough for a demo.

To scale: keep the `publish` / `current` interface and swap the internals for
a database or object storage.
"""
import threading
from typing import Optional

from pomomind.models import Course


class CourseStore:
    def __init__(self) -> None:
        self._course: Optional[Course] = None
        self._lock = threading.Lock()

    def publish(self, course: Course) -> None:
        with self._lock:
            self._course = course

    def current(self) -> Optional[Course]:
        with self._lock:
            return self._course

    def clear(self) -> None:
        with self._lock:
            self._course = None


course_store = CourseStore()
