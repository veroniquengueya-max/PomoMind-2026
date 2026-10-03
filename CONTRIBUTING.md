# Contributing

## Workflow

1. Fork, then branch from `main`: `git checkout -b feat/short-description`.
2. Set up: `pip install -r requirements-dev.txt`.
3. Make your change, add or update tests, run `pytest`.
4. Open a PR describing what changed and why. Keep PRs small and focused.

## Conventions

- **No logic in `app.py`.** It only wires modules together.
- **UI modules never import the Gemini SDK.** Go through `pomomind/services/`.
- **Services never import Streamlit.** They take plain arguments and return plain values.
- **No hard-coded user-facing strings.** Add a key to *both* languages in
  `locales.py` and use `t("screen.name")`. `tests/test_locales.py` fails if a key or
  `{placeholder}` is missing in one language.
- **Declare new session-state keys** in `DEFAULTS` in `state.py`.
- **Constants go in `config.py`**, prompts in `prompts.py`.
- Code, comments and docs in English.

## Adding a feature (example: a new student tab)

1. Add strings to `locales.py` (`en` and `fr`).
2. Write the screen as a function in `pomomind/ui/student.py` (or a new module).
3. If it needs the network or heavy logic, put that in `pomomind/services/`.
4. Add tests for anything that isn't pure UI.

## Tests

`pytest` runs without a Gemini key or a running Streamlit server. Test services and
data modules; keep UI modules thin so there is little to test in them.
