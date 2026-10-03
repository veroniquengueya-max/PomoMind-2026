# ARCHITECTURE: how the project is organised, and why

This describes the **structure** and the **decisions** behind it. For a list of what changed
in the code, see [CHANGES.md](CHANGES.md). For a guided tour of the code, see
[UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md).

## 1. The idea in one picture

```
            app.py                 <- starts everything, decides which screen to show
               |
        pomomind/ui/               <- screens: what the user sees and clicks
   login  sidebar  professor  student
               |
   uses -----> pomomind/services/  <- work behind the screens: Gemini, saved course
                   gemini.py   course_store.py
               |
   and the shared building blocks:
   config.py (numbers/names)   locales.py + i18n.py (text)   prompts.py (AI prompts)
   models.py (data types)      state.py (session memory)     auth.py (accounts)
```

**Dependency direction (who may import whom):**
`app.py` → `ui/*` → `services/*` → `models/config/prompts`.
Arrows never point backwards. `services/` never imports Streamlit; `ui/` never imports the Gemini SDK.
This keeps screens (easy to change, hard to test) apart from logic (easy to test, easy to reuse).

## 2. Why one big file became many small ones

The original mixed four jobs in one 150-line file: drawing the screen, remembering things,
calling the AI, and holding text in two languages. Mixed jobs mean that to change one
(say, the AI model) you must read all of them. The split gives each job one home:

| Job | Where |
|---|---|
| Show a screen | `ui/` |
| Call the AI, store the course | `services/` |
| Remember things during a session | `state.py` |
| Check who can log in | `auth.py` |
| Hold numbers and names that may change | `config.py` |
| Hold text people read | `locales.py` |
| Hold the AI's instructions | `prompts.py` |
| Describe the shapes of data | `models.py` |

## 3. File by file

### `app.py` (project root)
The entry point; you run `streamlit run app.py`. It only sets the page title/icon, initialises
the session memory, shows the language picker, then chooses: not logged in → login screen;
Professor → professor screen; otherwise → student screen. Kept in the root so the run command is unchanged.
*Decision:* no logic here, so a newcomer can read the whole flow of the app in ~20 lines.

### `pomomind/config.py`
Constants only: app name, languages, roles, XP values, timer length, anti-spam delay, Gemini model names,
the "valid" marker, and the sound URLs. *Why:* these literals were scattered through the code; now changing
the timer from 10 s to 25 min is a one-line edit. It imports nothing, so anything can import it safely.

### `pomomind/models.py`
Four small `dataclass`es: `User`, `Course`, `ApiSettings`, `Verdict`.
*Why dataclasses and not dicts:* a typo in a dict key (`user["rol"]`) fails late and silently; a typo in
`user.rol` fails immediately and editors can autocomplete. *Why `frozen=True`:* objects that cannot be
modified cannot be accidentally changed by another part of the app.

### `pomomind/state.py`
Everything about `st.session_state` (Streamlit's per-browser memory): the list of keys and defaults
(`DEFAULTS`), `init()`, `log_in()`, `log_out()`, `add_xp()`. *Why:* in the original, session keys were
created at the top and then read or changed in 20 places. Now every key is declared in one place, and
common changes go through named functions.

### `pomomind/auth.py`
The demo accounts and `authenticate(username, password, role)`, which returns a `User` or `None`.
*Decision:* isolated so it can be replaced by a real login system without touching any screen.
*Limit:* it is not secure (see Section 6).

### `pomomind/prompts.py`
The two instruction texts sent to Gemini (verify a course, create flashcards), as templates with
`{subject}` / `{count}` slots. *Why:* prompts are the most edited text in an AI app, and are easier
to review in one file than buried in function bodies.

### `pomomind/locales.py`
One dictionary per language (`"en"`, `"fr"`), same keys in both, e.g. `"login.title"`.
*Why:* the original wrote every sentence twice inline (`"..." if FR else "..."`), so adding a third
language meant editing every line of the app. Now you add one dictionary. A test checks that both
languages have the same keys and the same `{placeholders}`.
*Alternatives considered:* `gettext` (the standard tool). Rejected as too heavy for a project this size.

### `pomomind/i18n.py`
`t("key", name=value)` looks up the text in the current language and fills in the placeholders.
Kept separate from `locales.py` because `locales.py` is pure data (testable without Streamlit),
while `i18n.py` needs Streamlit to read the chosen language.

### `pomomind/services/gemini.py`
All contact with Gemini: `verify_course(...)` and `generate_flashcards(...)`, plus private helpers:
create the client, try models in order when the service is unavailable, wrap PDF bytes. Demo mode
is handled here, so screens do not need to know about it.

### `pomomind/services/course_store.py`
Holds the one course currently broadcast. A `CourseStore` class with `publish`, `current`, `clear`,
protected by a lock, plus one shared instance `course_store`.
*Why it exists:* `session_state` is private to each browser session, so it cannot pass data from a
professor to a student.
*Why a module-level object and not a database:* simplest thing that works for a demo, and every
Streamlit session in the same process sees the same object. *Alternatives considered:* `st.cache_resource`
(works the same but ties the store to Streamlit and makes testing harder); a file on disk (survives
restarts, but adds file handling and clean-up); a database (right for production, too big for now).
The `publish` / `current` interface is the seam where a database can be plugged in later.

### `pomomind/ui/login.py`, `sidebar.py`, `professor.py`, `student.py`
One file per screen, each with a `render()` entry (the sidebar has two functions because the language
picker shows before login and the account panel only after). They draw widgets, react to clicks,
call a service, show the result. The student file splits into `_timer_tab` and `_feed_tab`;
the professor file has `_broadcast` for the click handler. A leading underscore means "private to
this file".

### `tests/`
`test_auth.py`, `test_locales.py`, `test_course_store.py`. They test only code that has no screen and
needs no network or API key. *Decision:* screens are kept thin on purpose so there is little to test in them.

### Project files
`README.md` (how to run, what is where), `CONTRIBUTING.md` (rules for contributors), `requirements.txt`
(libraries to install), `requirements-dev.txt` (adds `pytest`), `pytest.ini` (tells pytest where the code is),
`.gitignore` (files git should not track, such as `.venv` and secrets), `docs/` (this folder).

## 4. Decisions worth knowing, in short

| # | Decision | Reason | Cost |
|---|---|---|---|
| D1 | Package called `pomomind`, entry file stays `app.py` | run command unchanged; code importable as `pomomind.xxx` | none |
| D2 | `ui/` vs `services/` split | UI is hard to test; logic should not depend on it | more files to learn |
| D3 | All text in `locales.py` | one place to translate; test catches missing keys | indirection: you look up a key to read a sentence |
| D4 | Dataclasses for shared data | catch typos early, document the data shape | four extra small classes |
| D5 | Shared in-memory course store | makes broadcast actually reach students | lost on restart; one course at a time |
| D6 | Send the PDF itself to Gemini for flashcards | the original summarised a file the AI never saw | uses more memory and tokens |
| D7 | Demo mode inside the service layer | screens stay free of `if demo` branches | fake data lives next to real calls |
| D8 | Constants in `config.py` | single place to tune | UI texts mentioning "10s" and "+50 XP" are still typed by hand |
| D9 | Keep original quirks (see CHANGES Part 8) | a restructure should not silently change behavior | known quirks remain |

## 5. How to add things

- **A new screen** → new file in `ui/` with a `render()` function; call it from `app.py`.
- **A new AI feature** → new function in `services/gemini.py`, prompt in `prompts.py`, button in the right screen.
- **A new language** → add a dictionary in `locales.py` with every key, and an entry in `LANGUAGES` in `config.py`.
- **A new session value** → add it to `DEFAULTS` in `state.py`.

## 6. Known limitations (honest list)

- Login is demo-only: accounts in code, passwords hashed with plain SHA-256 and no salt.
- One course for the whole server, kept in memory (lost on restart; not shared between several server processes).
- XP and streak are per session and never saved.
- The study streak is hard-coded to "3 days".
- Prompts are French, so flashcards are always generated in French.
- Gemini model name `gemini-3.8-flash` is unverified.
- No automated tests for the screens; only for pure modules.
