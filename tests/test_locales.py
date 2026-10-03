import string

from pomomind.config import LANGUAGES, SOUNDS
from pomomind.locales import STRINGS


def _placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_every_language_is_defined():
    assert set(STRINGS) == set(LANGUAGES)


def test_all_languages_have_the_same_keys():
    reference = set(STRINGS["en"])
    for lang, table in STRINGS.items():
        assert set(table) == reference, f"{lang} key mismatch: {set(table) ^ reference}"


def test_placeholders_match_across_languages():
    for key, text in STRINGS["en"].items():
        assert _placeholders(STRINGS["fr"][key]) == _placeholders(text), key


def test_every_sound_has_a_label():
    for lang in STRINGS.values():
        for sound in SOUNDS:
            assert f"sound.{sound}" in lang
