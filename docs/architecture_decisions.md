# Jarvis — Architecture Decisions

This file records important technical decisions so they are not repeatedly
reopened without evidence.

---

## ADR-001 — Preserve the Mark series

**Status:** Accepted

### Decision

Keep `jarvis.py`, `jarvis_mark2.py`, `jarvis_mark3.py`, and
`jarvis_mark4.py` as separate architectural milestones.

### Reasoning

The progression demonstrates how the project evolved:

- Mark 1: Groq text brain and tool calling
- Mark 2: Gemini migration
- Mark 3: ElevenLabs text-to-speech
- Mark 4: Gemini Live, asynchronous real-time voice and interruption

The historical progression has learning and portfolio value.

### Consequence

Future refactoring must not destructively replace or rewrite the historical
Mark files without an explicitly approved plan.

---

## ADR-002 — Use Gemini instead of Groq for the active brain

**Status:** Accepted

### Decision

The active implementation uses Gemini.

### Reasoning

The migration followed a repeated comparison of equivalent greeting and
tool-use inputs. Groq showed repeated tool-call formatting failures, while
Gemini performed more reliably in the observed benchmark.

### Consequence

Groq remains in the historical Mark 1 implementation but is not the default
brain for current development.

---

## ADR-003 — Use Gemini Live for Mark 4 voice

**Status:** Accepted

### Decision

Mark 4 uses Gemini Live for native audio input and audio output.

### Reasoning

Gemini Live provides a persistent bidirectional connection and supports
interruptible real-time interaction.

### Consequence

ElevenLabs remains relevant to the historical Mark 3 implementation but is
not part of Mark 4's active speech pipeline.

---

## ADR-004 — Keep personal configuration outside tracked source files

**Status:** Accepted

### Decision

- API keys live in `.env`.
- The real personal system prompt lives in `system_prompt.txt`.
- Conversation transcripts live in `conversation_log.txt`.
- Detailed private handoff material lives in `docs/private/`.

All of these locations are gitignored.

### Reasoning

The repository is public. Secrets, personal details and private conversations
must not be published.

### Consequence

Tracked template files must contain placeholders rather than real personal
information.

---

## ADR-005 — Require evidence before architectural fixes

**Status:** Accepted

### Decision

Do not implement a bug fix solely because it sounds plausible.

First gather runtime output, logs, reproducible inputs or another observable
signal.

### Reasoning

Past reliability decisions improved only after repeatable tests replaced
assumptions.

### Consequence

Agents must clearly label:

- confirmed behavior;
- hypotheses;
- proposed tests;
- verified results.

---

## ADR-006 — Coding agents plan before editing

**Status:** Accepted

### Decision

For meaningful changes, the coding agent must:

1. inspect the repository;
2. propose a scoped plan;
3. wait for approval;
4. implement only the approved work;
5. test it;
6. show the diff;
7. avoid committing unless explicitly asked.

### Reasoning

This keeps the user in control and exposes silent assumptions or unrelated
changes.

### Consequence

Broad requests such as “improve the entire repo” should be replaced with
small, single-purpose tasks.