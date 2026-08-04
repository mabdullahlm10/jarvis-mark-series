# Jarvis Project Instructions

## Project purpose

Jarvis is a production-oriented personal AI voice assistant and a learning
project.

The goals are:

1. Build an assistant that is genuinely reliable and useful.
2. Understand every important architectural layer rather than blindly
   accepting AI-generated code.
3. Learn how to supervise coding agents while retaining human review and
   technical ownership.

## Read before working

Before making technical claims or proposing changes:

1. Read `docs/current_status.md`.
2. Inspect the relevant source files.
3. Inspect Git status and recent Git history when useful.
4. If it exists locally, read
   `docs/private/jarvis_handoff_document.md` for detailed historical context.

The repository files and Git history are the source of truth.

The handoff document and previous conversations may contain outdated,
incomplete, or unverified claims.

## Working method

- Do not modify files immediately.
- First inspect the relevant code.
- Present a concise implementation plan.
- Wait for explicit approval before editing.
- Make one small, clearly scoped change at a time.
- Do not perform unrelated cleanup or refactoring.
- Do not silently change architectural decisions.
- After editing, run the relevant test or manual verification.
- Show and explain the resulting diff.
- Do not commit or push unless explicitly asked.

## Evidence standard

- Do not claim that something works until it has been run and verified.
- Distinguish confirmed behavior from assumptions and hypotheses.
- When diagnosing a bug, gather evidence before implementing a speculative fix.
- Preserve temporary debugging instrumentation only while it is actively needed.
- Remove temporary debug code before committing the final fix.

## Teaching method

For conceptually important new material:

1. Explain the problem being solved.
2. Ask the user to reason about the design.
3. Correct or sharpen the explanation.
4. Only then implement the important logic.

For mechanical setup, environment commands, or simple syntax corrections,
direct instructions are acceptable.

Every important code change should be understandable at a read-and-verify
level, not accepted as paste-and-pray code.

## Security and privacy

- Never expose, print, or commit API keys.
- API keys belong only in `.env`.
- Personal information belongs only in gitignored local files.
- The real personal system prompt belongs only in `system_prompt.txt`.
- `system_prompt.example.txt` must contain placeholders only.
- Conversation transcripts must remain gitignored.
- Verify `.gitignore` and staged changes before every commit involving
  configuration or personal data.

## Environment

- Operating system: Windows
- Shell: PowerShell
- Python virtual environment: `.venv`
- Activate it with `.venv\Scripts\activate`
- Use `python -m pip`, not bare `pip`
- Give Windows-compatible commands and paths

## Project-specific constraints

- Preserve `jarvis.py` and the Mark 2–4 files as architectural milestones.
- `jarvis_mark4.py` is currently the active and most advanced implementation.
- Do not restructure the Mark files without an approved refactoring plan.
- Do not commit a feature while it is known to be broken.
- Do not commit temporary debugging instrumentation.
- Avoid adding frameworks or abstractions without a demonstrated need.