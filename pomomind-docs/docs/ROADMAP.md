# ROADMAP: open work a contributor can pick up

Each item lists where to start. "Size": S = an hour or two, M = a day, L = several days.

## Verify / fix first
| Item | Size | Start in |
|---|---|---|
| Confirm the verification model name works with a real key (`gemini-3.8-flash`) and fix `VERIFY_MODELS` | S | `config.py` |
| Confirm flashcards work with `api_version="v1"`; remove it from the flashcard call if not | S | `services/gemini.py` `_client` |
| Replace placeholder audio URLs with real study sounds | S | `config.py` `SOUNDS` |
| Pin the real library versions used by the original | S | `requirements.txt` |

## Product
| Item | Size | Start in |
|---|---|---|
| One course per subject instead of a single shared course; list them all in the feed | M | `services/course_store.py`, `ui/student.py` |
| Persist courses (SQLite or files) so they survive restarts | M | `services/course_store.py` (keep `publish` / `current`) |
| Real study streak, persisted per student | M | `state.py`, `ui/sidebar.py` |
| Persist XP per user | M | new `services/` module, `state.py` |
| Flashcards in the UI language (the prompt is French only) | S | `prompts.py`, `services/gemini.py` |
| Non-blocking, longer Pomodoro (25 min) with pause | M | `ui/student.py` `_timer_tab` (the current loop blocks the page) |
| Derive "(10s)", "+50 XP", "+20 XP" in texts from `config.py` instead of typing them | S | `locales.py`, `ui/student.py` |

## Security
| Item | Size | Start in |
|---|---|---|
| Replace demo login with a real identity provider or salted hashing (bcrypt/argon2) | L | `auth.py` |
| Limit upload size and validate that the file is a real PDF | S | `ui/professor.py` |
| Keep API keys in `st.secrets` or environment variables instead of typing them each session | S | `ui/sidebar.py` |

## Quality
| Item | Size | Start in |
|---|---|---|
| Tests for `gemini.py` with a fake client (fallback on 503, other errors raised) | M | `tests/` |
| Tests for the screens with Streamlit's `AppTest` | M | `tests/` |
| Add a third language (shows that `locales.py` scales) | S | `locales.py`, `config.py` |
| CI: run `pytest` on every pull request | S | `.github/workflows/` |
