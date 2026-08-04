# Jarvis — Current Project Status

**Last updated:** 2026-07-25

**Verification state:** This status is based on the project handoff document
and the current Git diff. Runtime behavior still needs to be verified before
all claims are treated as confirmed.

## Active implementation

- Current active file: `jarvis_mark4.py`
- Architecture: Gemini Live API
- Input: live microphone audio
- Output: native streamed audio
- Concurrency: `asyncio`
- Current tools:
  - `get_weather`
  - `open_app`

## Current active bug

Jarvis's spoken responses are reportedly being written to
`conversation_log.txt`, but the user's spoken input is reportedly not being
logged.

The current leading hypothesis is that
`sc.input_transcription.finished` may not become `True` as expected.

This is still a hypothesis, not a confirmed cause.

## Current diagnostic instrumentation

The current uncommitted `jarvis_mark4.py` diff contains temporary debug
instrumentation:

`print(f"[DEBUG input_transcription] {sc.input_transcription!r}")`

This should remain until runtime evidence has been collected.

It must be removed before the transcript-logging feature is committed.

## Immediate next step after this documentation commit

1. Keep `jarvis_mark4.py` unstaged.
2. Run `jarvis_mark4.py`.
3. Speak one clear question.
4. Allow Jarvis to respond.
5. Stop the program.
6. Review:
   - the debug input-transcription output;
   - `conversation_log.txt`;
   - any terminal errors.
7. Use that evidence to confirm or reject the current hypothesis.
8. Only then propose the smallest fix.

## Other unresolved checks

- Verify that `system_prompt.example.txt` contains no personal information.
- Check whether the previously reported pronoun and title leftovers were fixed.
- Verify the current repository against the private handoff document.
- Confirm that no secrets or private files are tracked.

## Planned work that has not started

- Extracting shared logic into `tools.py` and `config.py`
- Automated tests
- Graceful async shutdown
- More tools
- Reactive visual interface
- MCP integration
- Long-session memory management
- Full README
