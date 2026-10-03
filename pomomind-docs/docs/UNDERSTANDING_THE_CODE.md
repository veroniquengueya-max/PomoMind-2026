# UNDERSTANDING THE CODE: a guided tour for someone who knows Python but not Streamlit

You already read loops, conditions, functions and imports. This guide gives you the
two or three Streamlit ideas you are missing, then walks through the project in the order
a user experiences it: login → professor uploads a PDF → student uses the timer → flashcards.

Open the files next to this guide. Quotes below are copied from the real code.

---

## Part 1: The one idea that explains everything about Streamlit

In normal Python, a script runs once, top to bottom, and ends.
In a game library like pygame, you write the loop yourself (`while running: ...`).

**In Streamlit, the framework runs your whole script from top to bottom again every time the user
does anything** (clicks a button, types in a box, changes a dropdown). That is the "loop", and
Streamlit runs it for you. Each run redraws the page.

From this follow all the odd-looking things in the code:

1. **Widgets return values.** `name = st.text_input("Name")` draws a box *and* returns what is in it
   *on this run*. There are no callbacks required.
2. **`st.button(...)` returns `True` only on the single run right after the click.**
   So `if st.button("Go"): ...` means "if the user just clicked Go". On the next run it is `False` again.
3. **Normal variables are forgotten between runs**, because the script restarts. To remember something
   (is the user logged in? how much XP?), use `st.session_state`, a dictionary that
   survives reruns *for one browser tab/session*. `st.session_state.xp` and
   `st.session_state["xp"]` mean the same thing.
4. **`st.rerun()`** says "stop now and start the script again". The code uses it after changing
   something that was already drawn earlier in the page (for example the XP number in the sidebar),
   so the page redraws with the new value.
5. **Modules are loaded once per server**, not once per run. A variable created at the top of a module
   (like `course_store`) is created once, and **all users' sessions share it**. `session_state` is
   private to one session; module-level variables are shared by everyone. This difference matters for the broadcast.

Mini example:

```python
import streamlit as st

if "count" not in st.session_state:      # first run only
    st.session_state.count = 0

if st.button("Add"):                     # True only on the run after a click
    st.session_state.count += 1

st.write(st.session_state.count)         # runs every time, shows the current value
```

Other Streamlit words you will see:
- `st.sidebar.xxx(...)` same as `st.xxx(...)` but drawn in the left panel.
- `with st.spinner("..."):` shows a spinner while the indented block runs.
- `st.tabs([...])` returns one container per tab; you draw inside with `with tab:`.
- `st.empty()` is a placeholder you can overwrite repeatedly (used for the countdown).
- `st.success / st.error / st.warning / st.info` coloured message boxes. `st.toast` is a small popup.

---

## Part 2: Map and reading order

Suggested reading order: `config.py` → `models.py` → `state.py` → `app.py` → `ui/login.py` + `auth.py`
→ `ui/sidebar.py` → `ui/professor.py` + `services/gemini.py` + `services/course_store.py`
→ `ui/student.py` → `locales.py` + `i18n.py` → `prompts.py` → `tests/`.

The decisions behind the structure are in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Part 3: The building blocks

### `config.py`: just named values
```python
ROLE_STUDENT = "Student"
ROLE_PROFESSOR = "Professor"
ROLES = (ROLE_STUDENT, ROLE_PROFESSOR)
STARTING_XP = 150
POMODORO_SECONDS = 10
```
Nothing to execute. Other files do `from pomomind.config import POMODORO_SECONDS`. If you want a
25-minute Pomodoro you would change `10` here.
`ROLES` is a **tuple** (like a list you cannot modify).
`VERIFY_MODELS = ("gemini-3.8-flash", "gemini-2.5-pro")` is the ordered list of AI models to try.

### `models.py`: shapes of data
```python
@dataclass(frozen=True)
class User:
    username: str
    role: str
    subject: Optional[str] = None
```
A **dataclass** is a class where Python writes `__init__` for you from the field list. `User("student", "Student")`
creates an object; you read `user.role`. `frozen=True` means you cannot change `user.role` afterwards.
`Optional[str] = None` means "a string, or `None` (the default)". Professors have a subject, students do not.

```python
@dataclass(frozen=True)
class ApiSettings:
    demo: bool = False
    key: str = ""

    @property
    def ready(self) -> bool:
        return self.demo or bool(self.key)
```
`@property` lets you write `api.ready` (no parentheses) as if it were a field. It is true when demo mode
is on, or when the key is not an empty string (`bool("")` is `False`).

`Course` (filename, subject, PDF bytes) and `Verdict` (approved yes/no, message) follow the same pattern.

### `state.py`: the session's memory
```python
DEFAULTS = {"logged_in": False, "role": ROLE_STUDENT, "username": "", "subject": None,
            "xp": STARTING_XP, "last_broadcast_ts": 0.0, "flashcards": None}

def init() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
```
`init()` loops over the defaults and, for each key, **only sets it if it does not exist yet**
(`setdefault`). So on the first run everything is created, and on later runs nothing is overwritten.
This runs at the top of every rerun, which is why it must not reset values.

Other helpers: `log_in(user)` stores the user's role, name and subject and sets `logged_in` to `True`;
`log_out()` calls `st.session_state.clear()`, which wipes everything (even the XP) so the next run starts
from defaults; `add_xp(n)` does `st.session_state.xp += n`.

---

## Part 4: Entry point: `app.py`

```python
st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON)

state.init()
sidebar.language_selector()

if not state.is_logged_in():
    login.render()
else:
    api = sidebar.account_panel()
    if st.session_state.role == ROLE_PROFESSOR:
        professor.render(api)
    else:
        student.render(api)
```
Read it as a story, on **every run**:
1. Set up the page.
2. Make sure the memory keys exist.
3. Draw the language picker.
4. Not logged in? Draw the login form.
5. Logged in? Draw the sidebar (which returns the API settings), then draw the professor or student screen.

This is the "router". It works because of Part 1: the script reruns after login, now `logged_in` is `True`,
so the `else` branch runs.

---

## Part 5: Login flow: `ui/login.py` and `auth.py`

```python
role = st.radio(t("login.role"), ROLES)
username = st.text_input(t("login.username"), placeholder="student, prof_bio, prof_cyber")
password = st.text_input(t("login.password"), type="password")

if st.button(t("login.button")):
    user = authenticate(username, password, role)
    if user:
        state.log_in(user)
        st.success(t("login.welcome"))
        st.rerun()
    else:
        st.error(t("login.error"))
```
- `st.radio(label, options)` returns the selected option (a role string).
- When the user clicks the button, `st.button` is `True` on that run, and `authenticate` is called.
- If the result is a `User` object, it is "truthy"; if `None`, it is "falsy". `if user:` handles both.
- After a successful login: store state, then `st.rerun()`. The script restarts, `is_logged_in()` is now true,
  and `app.py` shows the logged-in screens. (The `st.success` flashes and is replaced instantly. That is how the
  original behaved too.)

`auth.py`:
```python
def authenticate(username, password, role):
    record = _ACCOUNTS.get(username)
    if record is None:
        return None
    password_hash, user = record
    if hmac.compare_digest(hash_password(password), password_hash) and user.role == role:
        return user
    return None
```
Step by step: look up the username in the dictionary `_ACCOUNTS` (`.get` returns `None` if missing). If missing →
fail. Otherwise unpack `(password_hash, user)`. Hash what was typed with SHA-256 (`hash_password`) and compare it
to the stored hash. `hmac.compare_digest` is like `==` for strings but takes constant time, which avoids a
timing attack. Also the chosen role must match the account's role. Any failure returns `None`.
Nothing is ever stored in plain text here, but there is no salt, so it is for demos only.

---

## Part 6: The sidebar: `ui/sidebar.py`

Two functions:

**`language_selector()`**: draws the dropdown.
```python
st.sidebar.selectbox(t("language.label"), list(LANGUAGES),
                     format_func=LANGUAGES.get, key=LANGUAGE_KEY)
```
`LANGUAGES = {"en": "English", "fr": "French"}`. `list(LANGUAGES)` gives the *keys* `["en", "fr"]`,
which are what the widget stores. `format_func=LANGUAGES.get` says "to *display* a key, call `LANGUAGES.get(key)`",
so the user sees "English". `key="language"` stores the selected code in `st.session_state["language"]`,
where `i18n.py` finds it. Streamlit widgets with a `key` automatically save their value in session state.

**`account_panel()`**: shown after login:
- Draws the title, and for students the streak and XP metrics.
- `demo = st.sidebar.checkbox(...)`: `True` if ticked.
- `key = "" if demo else st.sidebar.text_input(...)`: **conditional expression**: if demo mode, no key box at
  all; otherwise show the box and take its text.
- If the logout button is clicked: `state.log_out()` then `st.rerun()` returns to the login screen.
- Returns `ApiSettings(demo=demo, key=key)`. Notice it *returns data*, which `app.py` passes to the screens.

---

## Part 7: The professor's broadcast: how the PDF gets saved

### `ui/professor.py`
```python
uploaded_pdf = st.file_uploader(t("professor.uploader"), type=["pdf"])
if st.button(t("professor.broadcast")):
    _broadcast(api, subject, uploaded_pdf)
```
`st.file_uploader` returns `None` until a file is chosen, then an object holding the file. `type=["pdf"]` limits choices.

`_broadcast` is a chain of checks, in this order:
```python
now = time.time()
if now - st.session_state.last_broadcast_ts < BROADCAST_COOLDOWN_SECONDS:
    st.warning(t("professor.spam"))
elif not api.ready:
    st.error(t("professor.missing_key"))
elif uploaded_pdf is None:
    st.warning(t("professor.missing_pdf"))
else:
    ...verify and publish...
```
This is an `if / elif / else` ladder: only the first true condition runs.
1. **Anti-spam**: `time.time()` is seconds since 1970. If less than 10 seconds have passed since the last
   successful broadcast, warn.
2. No API settings → error. 3. No file → warning. 4. Otherwise do the real work:

```python
with st.spinner(t("professor.spinner")):
    try:
        pdf_bytes = uploaded_pdf.getvalue()
        verdict = gemini.verify_course(api, subject, pdf_bytes)
        if verdict.approved:
            course_store.publish(Course(uploaded_pdf.name, subject, pdf_bytes))
            st.session_state.last_broadcast_ts = now
            st.success(t("professor.success", subject=subject))
        else:
            st.error(t("professor.blocked", reason=verdict.message))
    except Exception as err:
        st.error(t("professor.error", error=err))
```
- `getvalue()` returns the raw bytes of the uploaded file.
- The AI checks that the PDF matches the professor's subject (`verify_course`, below).
- If approved: **this is where the PDF is saved**: a `Course` object (file name, subject, bytes) is handed to
  `course_store.publish(...)`, and the cooldown timestamp is updated.
- If not approved: show the AI's reason.
- `try / except Exception`: if anything goes wrong (network, bad key), show the error instead of crashing.

### `services/course_store.py`: where "saved" really is
```python
class CourseStore:
    def __init__(self):
        self._course = None
        self._lock = threading.Lock()

    def publish(self, course):
        with self._lock:
            self._course = course

    def current(self):
        with self._lock:
            return self._course

course_store = CourseStore()
```
- It is a class holding **one** course in `self._course`. A leading underscore means "internal".
- The **lock**: Streamlit serves several users using several threads. A lock makes sure only one thread
  reads or writes at a time. `with self._lock:` takes the lock and releases it automatically at the end of the block.
- The last line creates the single shared object. Because the module is loaded once per server (Part 1, point 5),
  the professor's session and every student's session talk to the same `course_store`. That is the whole trick
  that makes the broadcast work.
- It is kept in RAM only. Restart the server and the course is gone.

### `services/gemini.py`: talking to the AI
```python
def verify_course(api, subject, pdf_bytes):
    if api.demo:
        time.sleep(1)
        return Verdict(True, VALID_MARKER)
    prompt = prompts.VERIFY_COURSE.format(subject=subject)
    text = _generate(_client(api.key), VERIFY_MODELS, [prompt, _pdf_part(pdf_bytes)])
    return Verdict(VALID_MARKER in text, text)
```
- Demo mode: pretend for 1 second, return "approved".
- Otherwise: fill the prompt template with the subject (`.format`), send the prompt and the PDF to Gemini,
  and approve only if the answer contains the text `[VALIDE]`. `VALID_MARKER in text` is a substring test
  giving `True` or `False`.

The fallback loop:
```python
def _generate(client, models, contents):
    for model in models[:-1]:
        try:
            return client.models.generate_content(model=model, contents=contents).text
        except Exception as err:
            if not _is_unavailable(err):
                raise
    return client.models.generate_content(model=models[-1], contents=contents).text
```
`models[:-1]` means "all models except the last". For each, try it; if it works, `return` the text and
stop. If it fails with an "unavailable" error (503), the loop continues to the next model. If it fails with
anything else, `raise` re-throws the error. If every earlier model was unavailable, the last model is tried
without protection, so its error propagates. This is the same logic as the original's nested try/except.

`_pdf_part` wraps raw bytes into a Gemini `Part` with MIME type `application/pdf`.

---

## Part 8: The student screen: `ui/student.py`

```python
def render(api):
    st.title(t("student.title"))
    course = course_store.current()
    if course:
        st.info(t("student.notification", subject=course.subject, filename=course.filename))
    timer_tab, feed_tab = st.tabs([t("student.tab_timer"), t("student.tab_feed")])
    with timer_tab:
        _timer_tab()
    with feed_tab:
        _feed_tab(api)
```
It reads the shared store: if a course exists, show the notification. Then two tabs; the `with` block says
"draw the following inside this tab".

### The timer
```python
sound = st.selectbox(t("timer.sound"), list(SOUNDS), format_func=lambda k: t(f"sound.{k}"))
if SOUNDS[sound]:
    st.audio(SOUNDS[sound], format="audio/mp3", start_time=0)
```
`SOUNDS` is a dict `{"silence": None, "lofi": "<url>", "binaural": "<url>"}`. The dropdown stores the key and
shows a translated label through `lambda k: t(f"sound.{k}")` (a small anonymous function that builds
`"sound.lofi"` and looks it up). `if SOUNDS[sound]:` is false for `None` (silence), so no player is drawn.

```python
if st.button(t("timer.start")):
    display = st.empty()
    for remaining in range(POMODORO_SECONDS, 0, -1):
        display.metric(t("timer.focus"), f"00:{remaining:02d}")
        time.sleep(1)
    st.balloons()
    state.add_xp(XP_POMODORO)
    st.success(t("timer.done"))
    st.rerun()
```
- `range(10, 0, -1)` counts 10, 9, ..., 1.
- Each second, the same placeholder is overwritten (`display.metric`) with the new time. `:02d` pads to two digits (`07`).
- `time.sleep(1)` pauses the script, so the page is busy until the countdown ends. That is a simple but blocking approach.
- After 10 seconds: balloons, add 50 XP, then `st.rerun()` so the sidebar shows the new XP.

### The course feed and flashcards
```python
course = course_store.current()
if course is None:
    st.write(t("feed.empty"))
    return
```
No course → say so, and `return` leaves the function early.

```python
if st.button(t("feed.flashcards_button")):
    if not api.ready:
        st.error(t("feed.missing_key"))
    else:
        with st.spinner(t("feed.spinner")):
            try:
                text = gemini.generate_flashcards(api, course)
            except Exception as err:
                st.error(t("feed.error", error=err))
            else:
                st.session_state.flashcards = (course.filename, text)
                state.add_xp(XP_FLASHCARDS)
                st.toast(t("feed.success"))
                st.rerun()
```
New Python feature here: `try / except / else`. The `else` block runs only if the `try` raised no error.
On success the result is stored as a **tuple** `(filename, text)` in session state, XP is added, a toast pops up,
and the page reruns. Because the text is in session state, it survives the rerun and is drawn by:
```python
saved = st.session_state.flashcards
if saved and saved[0] == course.filename:
    st.markdown("---")
    st.write(saved[1])
```
`saved[0]` is the file name: the cards are shown only if they belong to the course currently broadcast.

`generate_flashcards` (in `gemini.py`) sends the PDF and a prompt asking for 3 cards; in demo mode it returns fixed text.

---

## Part 9: Text and languages: `locales.py`, `i18n.py`

```python
STRINGS = {
    "en": {"login.title": "🔒 PomoMind AI - Portal", ...},
    "fr": {"login.title": "🔒 PomoMind AI - Portail", ...},
}
```
A dictionary of dictionaries: `STRINGS["fr"]["login.title"]`. The dotted key is just a string
naming the screen and the item.

```python
def t(key, **values):
    text = STRINGS[current_language()][key]
    return text.format(**values) if values else text
```
- `**values` collects keyword arguments into a dict: `t("sidebar.title", role="Student")` gives `{"role": "Student"}`.
- `text.format(**values)` fills `{role}` inside the text.
- `x if cond else y` is Python's one-line conditional.
- `current_language()` reads `st.session_state.get("language", "en")`, defaulting to English.

So the language picker changes `session_state["language"]`; Streamlit reruns; every `t(...)` call now returns the other language.

---

## Part 10: Follow one click from start to finish

Student clicks "Start the Session":
1. Streamlit reruns `app.py` from the top. `state.init()` finds all keys already exist.
2. `is_logged_in()` is true → `sidebar.account_panel()` draws; `student.render(api)` runs.
3. `_timer_tab` runs; this time `st.button(...)` returns `True` because of the click.
4. The `for` loop counts down, overwriting the placeholder each second.
5. XP goes from 150 to 200 in `session_state`. `st.rerun()` restarts the script.
6. On the new run, `account_panel` draws the metric with the new XP: `200 XP`.

---

## Part 11: Glossary of the Python features used

| Term | Example in the project | Meaning |
|---|---|---|
| `dataclass` | `models.py` | class whose `__init__` is generated from fields |
| `frozen=True` | `models.py` | fields cannot be changed after creation |
| `Optional[str]` | `models.py` | a `str` or `None` |
| `@property` | `ApiSettings.ready` | a method used like an attribute |
| tuple | `ROLES`, `VERIFY_MODELS` | list that cannot be modified |
| `dict.get(k)` | `_ACCOUNTS.get(username)` | value or `None` if missing |
| slicing `[:-1]` | `models[:-1]` | everything except the last item |
| `with` | `with self._lock:` | set up and always clean up a resource |
| `try/except/else` | `_feed_tab` | `else` runs only if no error |
| `raise` | `_generate` | re-throw the current error |
| `**kwargs` | `t(key, **values)` | collect/spread keyword arguments |
| lambda | `format_func=lambda k: ...` | tiny anonymous function |
| conditional expr. | `"" if demo else ...` | `a if cond else b` |
| f-string | `f"00:{remaining:02d}"` | text with values inside `{}`; `:02d` pads to 2 digits |
| `hmac.compare_digest` | `auth.py` | safe string comparison |
| `threading.Lock` | `course_store.py` | stops two threads touching data at once |
| leading `_` | `_broadcast`, `_course` | "internal, not for other files" |

---

## Part 12: Try it yourself (in this order)

1. In `config.py`, change `POMODORO_SECONDS` to 5. Run the timer. (Notice the button text still says "10s", which lives in `locales.py`.)
2. Add a new sound key `"rain"` in `SOUNDS` and the labels `"sound.rain"` in both languages in `locales.py`. Run `tests/` and watch what fails if you forget one language.
3. Add a student metric in `ui/sidebar.py` (for example the logged-in username).
4. Change `FLASHCARD_COUNT` to 5 and read the cards in demo mode vs real mode. Why does demo mode not change?
5. Put a `print("RERUN")` at the top of `app.py`, click around, and count the reruns in the terminal. This makes Part 1 concrete.
6. Hard: make `CourseStore` keep one course *per subject* (a dict), then show every course in the feed.
