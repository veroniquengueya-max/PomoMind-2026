# PomoMind AI

A Streamlit study app. Students run Pomodoro sessions with ambient sound and turn
official course PDFs into short flashcards. Professors upload a PDF; a Gemini agent
checks it matches their subject before it is broadcast to the class.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
pytest
```

Tick **Demo Mode** in the sidebar to run without a Gemini API key.

Demo accounts (role must match the one you pick on the login screen):

| Username     | Password        | Role      |
|--------------|-----------------|-----------|
| `student`    | `student123`    | Student   |
| `prof_bio`   | `prof_bio123`   | Professor |
| `prof_cyber` | `prof_cyber123` | Professor |

## Project layout

```
app.py                      Entry point: page config + routing only
pomomind/
  config.py                 Constants: roles, XP, models, sounds
  models.py                 Dataclasses: User, Course, ApiSettings, Verdict
  state.py                  st.session_state keys and helpers
  auth.py                   Demo authentication
  prompts.py                LLM prompt templates
  locales.py                All UI text, English + French
  i18n.py                   t("key") translation helper
  services/                 Logic with no UI code
    gemini.py               Gemini calls (verify_course, generate_flashcards)
    course_store.py         Shared "current course" store
  ui/                       One module per screen, each exposes render()
    login.py  sidebar.py  professor.py  student.py
tests/                      pytest suite (no Streamlit or network needed)
```

Rule of thumb: **`ui/` talks to the user, `services/` talks to the outside world,
`config.py` / `locales.py` / `prompts.py` hold the things you tweak most.**

## Where do I change...?

| I want to...                         | Edit                                    |
|--------------------------------------|-----------------------------------------|
| Change text or translations          | `pomomind/locales.py`                   |
| Add a language                       | `locales.py` + `LANGUAGES` in `config.py` |
| Tune XP, timer length, models, sounds| `pomomind/config.py`                    |
| Change an AI prompt                  | `pomomind/prompts.py`                   |
| Add or edit a screen                 | `pomomind/ui/`                          |
| Swap the course storage for a DB     | `pomomind/services/course_store.py`     |
| Replace the demo login               | `pomomind/auth.py`                      |

## Known limitations

- Auth is demo-only (hard-coded accounts, unsalted SHA-256). Do not deploy as is.
- The course store is in-memory and per server process: it resets on restart and
  does not work across multiple server instances.
- Student XP and streak are per session and not persisted.
- `VERIFY_MODELS` in `config.py` should be checked against the model names your
  API key can actually use.

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.
