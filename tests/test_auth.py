from pomomind.auth import authenticate
from pomomind.config import ROLE_PROFESSOR, ROLE_STUDENT


def test_valid_student_login():
    user = authenticate("student", "student123", ROLE_STUDENT)
    assert user is not None and user.role == ROLE_STUDENT


def test_valid_professor_login_has_subject():
    user = authenticate("prof_bio", "prof_bio123", ROLE_PROFESSOR)
    assert user is not None and user.subject == "Biologie"


def test_wrong_password_rejected():
    assert authenticate("student", "nope", ROLE_STUDENT) is None


def test_wrong_role_rejected():
    assert authenticate("student", "student123", ROLE_PROFESSOR) is None


def test_unknown_user_rejected():
    assert authenticate("ghost", "x", ROLE_STUDENT) is None
