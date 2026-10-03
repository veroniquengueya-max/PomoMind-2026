# HANDOFF: short summary for the project owner

**What happened:** the single-file `app.py` was reorganised into a package (`pomomind/`) with
a README, contributor guide, tests and these docs. Features, screens, texts and demo accounts are the same.

**Structure:** `app.py` (entry) → `pomomind/ui/` (screens) → `pomomind/services/` (Gemini, shared course).
Numbers in `config.py`, text in `locales.py`, AI prompts in `prompts.py`. Map of old line → new file:
[CHANGES.md](CHANGES.md) Part 2.

**Behavior that is NOT identical to your original (details in CHANGES.md Part 1):**
1. A broadcast course is now stored in a shared in-memory store so students can actually see it (originally it lived in per-session memory and was wiped on logout).
2. Flashcards now send the real PDF to Gemini (originally only the file name and subject).
3. Flashcards stay on screen after generation (originally erased by an immediate `st.rerun()`); the success message is a toast.
4. Demo mode now covers flashcards.
5. The flashcard Gemini client now uses `api_version="v1"` like the verification client. **Untested with a real key.**
6. Timer shows `00:10` instead of `00:010`; the two sound options now have two different placeholder MP3 URLs.
7. Some French-only texts now have English versions.

**To verify in about 10 minutes:** follow the checklist in CHANGES.md Part 10, including one run with a real API key.

**Not verified:** the model name `gemini-3.8-flash`, the `requirements.txt` version numbers, the placeholder audio URLs.

**Unchanged on purpose:** hard-coded demo accounts, fixed "3 days" streak, French prompts, other quirks listed in CHANGES.md Part 8.
