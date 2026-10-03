# CHANGES: everything that was changed from the original `app.py`

The original was one file of about 150 lines. This document lists **every** change made
when it was split into a package, from renamed variables to new classes, so that nobody
has to guess. If you only read one section, read **Part 1**.

How to read this file:
- "Original line N" always refers to the original single-file `app.py`.
- Part 1 = changes that alter what the app does. Part 2 = where each original piece went.
  Parts 3-7 = structural, mechanical and cosmetic changes. Part 8 = things deliberately left alone.
  Part 9 = things I could not verify. Part 10 = a checklist to confirm "same behavior".

---

## Part 1: Behavior changes (the app now acts differently here)

### 1.1 The broadcast course is now shared across all users
- **Before** (original lines 82, 91-92, 111): after a professor broadcast a course, its name and
  subject were stored in `st.session_state` (`prof_pdf_name`, `prof_pdf_subject`).
  `session_state` belongs to one browser session, and logout runs `st.session_state.clear()`
  (line 48), so a student could never see a professor's upload.
- **After**: the course is saved in `pomomind/services/course_store.py` (`course_store.publish(...)`),
  a module-level object shared by every session in the same server process.
- **Side effects**: any professor's upload replaces the previous one for everyone (only one
  course exists at a time). The course disappears when the server restarts.

### 1.2 Flashcards are generated from the real PDF
- **Before** (lines 135-138): Gemini received only text: the subject and the file name.
  The PDF itself was never sent, so the model had nothing to summarise and would invent content.
- **After** (`services/gemini.py`, `generate_flashcards`): the PDF bytes are sent along with the prompt,
  the same way the verification step already did.
- **Side effect**: the PDF bytes are now kept in server memory inside the `Course` object.

### 1.3 Flashcards no longer vanish, and the success message is a toast
- **Before** (lines 140-144): the app wrote the flashcards to the screen, then immediately called
  `st.rerun()`, which redraws the page and erased them.
- **After** (`ui/student.py`, `_feed_tab`): the text is saved in `st.session_state.flashcards` as a
  pair `(filename, text)` and displayed on every run while that course is current.
  The "Flashcards generated! +20 XP" message is now `st.toast(...)` instead of `st.success(...)`.
  The `st.rerun()` is kept so the XP number in the sidebar refreshes.

### 1.4 Demo mode now also works for flashcards
- **Before**: demo mode set the API key to the string `"DEMO"`. Verification had a special
  case for it (line 68), but flashcards did not, so they called Gemini with a fake key and failed.
- **After**: `gemini.generate_flashcards` returns fixed example cards when `api.demo` is true.

### 1.5 The flashcard client now uses `api_version="v1"`
- **Before** (line 122): `genai.Client(api_key=...)` with the SDK's default API version.
- **After**: both Gemini calls use `genai.Client(api_key=..., http_options=types.HttpOptions(api_version="v1"))`.
  This is what the verification step (line 71) already used. **Untested with a real key.**
  If flashcards fail with a real key, this is the first thing to check.

### 1.6 Timer display and sound options
- **Timer**: the original used `f"00:0{i}"`, which printed `00:010` when `i` was 10. Now
  `f"00:{remaining:02d}"` prints `00:10`.
- **Sounds**: both options ("Lo-Fi study" and the binaural one) pointed at `"https://soundhelix.com"`,
  which is a web page, not an audio file (original line 100). They now point at two different
  placeholder MP3 files listed in `config.py` (`SOUNDS`). Replace them with real tracks.

### 1.7 Some text now exists in English that was French-only
Original strings with no English version, now translated:

| Where | French (unchanged) | New English |
|---|---|---|
| Timer tab title (line 94) | ⏳ Chrono Pomodoro & Musique | ⏳ Pomodoro Timer & Music |
| Timer heading (line 97) | 📈 Session Focus Pomodoro | 📈 Pomodoro Focus Session |
| Shared document line (line 112) | 📄 **Document partagé :** ... | 📄 **Shared document:** ... |
| Professor error (line 86) | Erreur : ... | Error: ... |
| Flashcard error (line 147) | Erreur IA : ... | AI error: ... |

All other texts, in both languages, are identical to the original.

---

## Part 2: Where each part of the original went

| Original lines | What it was | Now lives in |
|---|---|---|
| 1-3 | imports | split: each module imports what it needs (`hashlib` → `auth.py`, `genai` → `services/gemini.py`, `time` → `ui/professor.py`, `ui/student.py`, `services/gemini.py`) |
| 5 | `st.set_page_config` | `app.py` (title/icon values from `config.py`) |
| 7-9 | session-state defaults | `state.py` (`DEFAULTS`, `init()`) |
| 11-12 | language picker + `FR` flag | `ui/sidebar.py` `language_selector()`, `i18n.py`; the `FR` flag no longer exists |
| 15-21 | login form | `ui/login.py` |
| 24-28 | user accounts | `auth.py` (`_ACCOUNTS`) |
| 29-35 | password check, login success/failure | `auth.py` `authenticate()`, `ui/login.py`, `state.log_in()` |
| 39-42 | sidebar title and student metrics | `ui/sidebar.py` `account_panel()` |
| 44-45 | demo checkbox and API key field | `ui/sidebar.py` → returns an `ApiSettings` object |
| 47-48 | logout | `ui/sidebar.py` + `state.log_out()` |
| 51-66 | professor screen and checks | `ui/professor.py` (`render`, `_broadcast`) |
| 67-79 | AI verification and model fallback | `services/gemini.py` (`verify_course`, `_generate`) |
| 73 | verification prompt | `prompts.py` `VERIFY_COURSE` |
| 75, 78 | model names | `config.py` `VERIFY_MODELS` |
| 81-86 | approve / block result | `ui/professor.py` `_broadcast` |
| 90-92 | student title and notification | `ui/student.py` `render()` |
| 94 | tabs | `ui/student.py` `render()` |
| 96-107 | timer tab | `ui/student.py` `_timer_tab()` |
| 109-149 | course feed and flashcards | `ui/student.py` `_feed_tab()` |
| 122-138 | flashcard Gemini call | `services/gemini.py` `generate_flashcards()` |
| 125-132 | flashcard prompt | `prompts.py` `FLASHCARDS` |
| 136 | flashcard model name | `config.py` `FLASHCARD_MODEL` |
| all `"fr" if FR else "en"` pairs | UI text | `locales.py` |

---

## Part 3: New classes (there were none in the original)

All in `pomomind/models.py` except `CourseStore`. All four dataclasses are `frozen=True`, meaning
their fields cannot be changed after creation.

| Class | Fields | Replaces |
|---|---|---|
| `User` | `username`, `role`, `subject` | the inner dicts of the `users` dictionary (line 24-28) |
| `Course` | `filename`, `subject`, `content` (PDF bytes) | session keys `prof_pdf_name`, `prof_pdf_subject` (+ new `content`) |
| `ApiSettings` | `demo`, `key`, property `ready` | the variable `api_key_input` and its `"DEMO"` magic string; `ready` replaces `not api_key_input` checks |
| `Verdict` | `approved`, `message` | the `"[VALIDE]" in ai_text` check (line 81) and `ai_text` |
| `CourseStore` (`services/course_store.py`) | `publish()`, `current()`, `clear()`, a private lock | new, see 1.1. `course_store` is the one instance |

## Part 4: New functions (the original had none)

- `state.py`: `init`, `is_logged_in`, `log_in`, `log_out`, `add_xp`
- `auth.py`: `hash_password`, `authenticate`
- `i18n.py`: `current_language`, `t`
- `services/gemini.py`: `_client`, `_is_unavailable`, `_generate`, `_pdf_part`, `verify_course`, `generate_flashcards`
- `ui/login.py`: `render`
- `ui/sidebar.py`: `language_selector`, `account_panel`
- `ui/professor.py`: `render`, `_broadcast`
- `ui/student.py`: `render`, `_timer_tab`, `_feed_tab`

## Part 5: Renames

| Before | After |
|---|---|
| `dernier_clic_prof` (session key) | `last_broadcast_ts` |
| `prof_pdf_name`, `prof_pdf_subject` (session keys) | removed; data is in `Course` (`filename`, `subject`) |
| `temps_actuel` | `now` |
| `uploaded_pdf` | `uploaded_pdf` (same) |
| `api_key_input` | `ApiSettings` (`api.key`, `api.demo`, `api.ready`) |
| `ai_text` | `Verdict.message` / `text` |
| `i` (timer loop) | `remaining` |
| `t` (the `st.empty()` placeholder, line 104) | `display` (because `t` is now the translation function) |
| `role_choice`, `username_input`, `password_input` | `role`, `username`, `password` |
| `url_sound`, `sound` (display names) | `SOUNDS` keys `"silence"`, `"lofi"`, `"binaural"` |

New session key: `flashcards`.

## Part 6: Values moved into `config.py`

These were literals scattered in the code; the values themselves are unchanged unless noted.

| Constant | Value | Original |
|---|---|---|
| `STARTING_XP` | 150 | line 8 |
| `XP_POMODORO` | 50 | line 107 |
| `XP_FLASHCARDS` | 20 | line 142 |
| `POMODORO_SECONDS` | 10 | line 105 |
| `BROADCAST_COOLDOWN_SECONDS` | 10 | line 59 |
| `VERIFY_MODELS` | `("gemini-3.8-flash", "gemini-2.5-pro")` | lines 75, 78 |
| `FLASHCARD_MODEL` | `"gemini-2.5-flash"` | line 136 |
| `FLASHCARD_COUNT` | 3 | line 127 ("exactement 3") |
| `VALID_MARKER` | `"[VALIDE]"` | lines 69, 81 |
| `ROLE_STUDENT`, `ROLE_PROFESSOR`, `ROLES` | `"Student"`, `"Professor"` | lines 8, 19, 25-27, 40, 51, 89 |
| `SOUNDS` | see 1.6 | lines 98-100 |

Note: the UI text still says "(10s)" and "+50 XP" / "+20 XP" as plain text in `locales.py`.
If you change `POMODORO_SECONDS` or the XP constants, update those texts too (they are not computed).

## Part 7: Mechanical changes that keep the same behavior

- **Language**: `FR = language == "French"` plus inline `"fr" if FR else "en"` (and, in the student
  feed, `language == "French"`) are replaced by `t("key")` reading the language code stored
  under `st.session_state["language"]`. The selector now has `key="language"` and stores
  `"en"` / `"fr"`, showing "English" / "French" through `format_func`.
- **Password check**: the original hashed the typed password and also hashed the stored plain-text
  password, then compared (line 30). Now `auth.py` stores the SHA-256 hashes directly and compares with
  `hmac.compare_digest`. Same result for the same credentials. The hashed values were computed from
  the original passwords.
- **Role + credentials check** moved from one long `if` into `authenticate()` returning a `User` or `None`.
- **PDF reading**: `uploaded_pdf.read()` → `uploaded_pdf.getvalue()` (same bytes, but safe to call twice).
- **Model fallback**: the nested `try/except` (lines 74-79) became a loop in `_generate`. Same rule:
  go to the next model only for errors containing "503" or "UNAVAILABLE"; any other error is raised.
- **Sound selection**: the selectbox used to store the displayed (translated) label and compare strings
  (lines 98-100). It now stores a stable key and translates the label with `format_func`.
- **Timer format**: see 1.6.
- **Sidebar metrics, logout, title**: same widgets, same order, text now from `t()`.
- **Error handling in professor flow**: the broad `try/except Exception` is kept (shows the error text).
- **Formatting**: long one-line `if ...: x; y` statements were split into normal multi-line code.

## Part 8: Deliberately NOT changed (quirks kept on purpose)

- Study streak is a fixed "3 days" (line 41). It is not computed.
- Demo accounts and passwords are hard-coded. Passwords are hashed without a salt. Login is for demos only.
- The anti-spam timestamp is only updated after a *successful* broadcast (line 82).
- Prompts are in French, and the flashcards always come out in French even when the UI is English.
- The model name `gemini-3.8-flash` is unchanged and unverified (see Part 9).
- After login, `st.success("Welcome")` is followed by `st.rerun()`, so the message is never seen (lines 32-33).
- The timer blocks the page with `time.sleep` in a loop, then reruns.
- Flashcards have no model fallback (only one model), as in the original.
- XP and streak are lost on logout or refresh, and are per-session.
- The subject name "Biologie" is French even in English mode.

## Part 9: Things I could not verify

- Whether `gemini-3.8-flash` exists. If it doesn't, professor verification fails with an error.
- Whether `api_version="v1"` works for flashcards (see 1.5).
- The SoundHelix URLs in `SOUNDS` are placeholders I chose; I could not test them (no network here).
- `requirements.txt` version numbers (`streamlit>=1.40`, `google-genai>=1.0`) are my estimates, not
  the versions the original ran on. If the owner knows their versions, pin those instead.
- I never ran the app myself (Streamlit was not installed in my environment). I tested only the
  pure modules (auth, locales, course store) with a plain Python runner; I could not run `pytest` there.
  The project owner you work with has run the tests and the app on their side.

## Part 10: Checklist: "does it still behave the same?"

Run the original `app.py` and this version one after the other (different ports:
`streamlit run app.py --server.port 8501`). In both, use demo mode.

1. Log in as `student` / `student123` (role Student). ✔ sidebar shows streak "3 days", score 150 XP.
2. Wrong password → red error. Right password with the wrong role → red error.
3. Start the timer → 10-second countdown, balloons, XP becomes 200. *(Expected difference: `00:10` vs `00:010`.)*
4. Log out, log in as `prof_bio` / `prof_bio123` (role Professor). ✔ dashboard shows "Biologie".
5. Click broadcast with no PDF → warning. With a PDF → success. Click again within 10 s → anti-spam warning.
6. Log out, log in as student. **Expected difference:** the new version shows the teacher notification; the original does not (1.1).
7. In the Course Feed, click the flashcards button. **Expected difference:** the original errors in demo mode; the new one shows demo cards that stay on screen (1.3, 1.4).
8. Switch language to French at every step and compare texts.
9. With a **real** API key (not demo): check that professor verification and flashcards both work. This covers 1.5 and the model name.
