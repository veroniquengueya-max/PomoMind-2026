"""All tunable constants live here. No Streamlit imports, no logic."""

APP_NAME = "PomoMind AI"
APP_ICON = "🔒"

# --- Languages -------------------------------------------------------------
DEFAULT_LANGUAGE = "en"
LANGUAGES = {"en": "English", "fr": "French"}

# --- Roles -----------------------------------------------------------------
ROLE_STUDENT = "Student" 
ROLE_PROFESSOR = "Professor"
ROLES = (ROLE_STUDENT, ROLE_PROFESSOR)

# --- Gamification ----------------------------------------------------------
STARTING_XP = 150
XP_POMODORO = 50
XP_FLASHCARDS = 20
POMODORO_SECONDS = 10  # demo length; set to 25 * 60 for a real Pomodoro

# --- Professor workflow ----------------------------------------------------
BROADCAST_COOLDOWN_SECONDS = 10

# --- Gemini ----------------------------------------------------------------
# Models are tried in order; the next one is used only on 503/UNAVAILABLE.
VERIFY_MODELS = ("gemini-3.8-flash", "gemini-2.5-pro")
FLASHCARD_MODEL = "gemini-2.5-flash"
FLASHCARD_COUNT = 3
VALID_MARKER = "[VALIDE]"  # the verification prompt asks the model to answer with this

# --- Study sounds ----------------------------------------------------------
# key -> audio URL (None = silence). Labels come from locales.py ("sound.<key>").
# NOTE: placeholder tracks; swap in real lo-fi / binaural audio.
SOUNDS = {
    "silence": None,
    "lofi": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "binaural": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
}
