"""All Gemini access. UI modules call these functions and never touch the SDK."""
import time

from google import genai
from google.genai import types

from pomomind import prompts
from pomomind.config import (
    FLASHCARD_COUNT,
    FLASHCARD_MODEL,
    VALID_MARKER,
    VERIFY_MODELS,
)
from pomomind.models import ApiSettings, Course, Verdict

DEMO_FLASHCARDS = """\
### 🧬 Demo Flashcard 1
Ceci est une réponse de démonstration (mode démo, aucun appel API).

### 🚕 Demo Flashcard 2
Comme un taxi de Yaoundé : on ne part que quand tout est prêt.

### 🥣 Demo Flashcard 3
Comme les beignets-haricots : simple, efficace, addictif.
"""


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version="v1"))


def _is_unavailable(err: Exception) -> bool:
    return "503" in str(err) or "UNAVAILABLE" in str(err)


def _generate(client: genai.Client, models: tuple, contents: list) -> str:
    """Try each model in order, falling back only when the service is unavailable."""
    for model in models[:-1]:
        try:
            return client.models.generate_content(model=model, contents=contents).text
        except Exception as err:
            if not _is_unavailable(err):
                raise
    return client.models.generate_content(model=models[-1], contents=contents).text


def _pdf_part(pdf_bytes: bytes) -> types.Part:
    return types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")


def verify_course(api: ApiSettings, subject: str, pdf_bytes: bytes) -> Verdict:
    """Ask the model whether the PDF matches the professor's subject."""
    if api.demo:
        time.sleep(1)
        return Verdict(True, VALID_MARKER)
    prompt = prompts.VERIFY_COURSE.format(subject=subject)
    text = _generate(_client(api.key), VERIFY_MODELS, [prompt, _pdf_part(pdf_bytes)])
    return Verdict(VALID_MARKER in text, text)


def generate_flashcards(api: ApiSettings, course: Course) -> str:
    """Turn the broadcast course PDF into short flashcards (markdown text)."""
    if api.demo:
        return DEMO_FLASHCARDS
    prompt = prompts.FLASHCARDS.format(count=FLASHCARD_COUNT)
    return _generate(_client(api.key), (FLASHCARD_MODEL,), [prompt, _pdf_part(course.content)])
