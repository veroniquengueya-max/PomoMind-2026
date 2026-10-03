from pomomind.models import Course
from pomomind.services.course_store import CourseStore


def test_empty_store_has_no_course():
    assert CourseStore().current() is None


def test_publish_replaces_current_course():
    store = CourseStore()
    store.publish(Course("a.pdf", "Biologie", b"1"))
    store.publish(Course("b.pdf", "Cybersecurity", b"2"))
    assert store.current().filename == "b.pdf"


def test_clear():
    store = CourseStore()
    store.publish(Course("a.pdf", "Biologie", b"1"))
    store.clear()
    assert store.current() is None
