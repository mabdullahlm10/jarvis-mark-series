# Jarvis — Current Project Status

**Last updated:** 2026-08-06

**Verification state:** The transcript-logging feature and user-buffer fallback
have been verified through a live runtime test.

## Active implementation

- Current active file: `jarvis_mark4.py`
- Architecture: Gemini Live API
- Input: live microphone audio
- Output: native streamed audio
- Concurrency: `asyncio`
- Current tools:
  - `get_weather`
  - `open_app`

## Recently resolved — User transcription logging

Jarvis previously logged its own spoken responses but did not log the user's
spoken input.

Runtime evidence showed that Gemini supplied input-transcription text without
supplying a `finished=True` signal for the observed user turn. As a result,
the text accumulated in `user_buffer`, but the original completion condition
did not flush it to `conversation_log.txt`.

A fallback was added:

- The existing `input_transcription.finished` path remains.
- When Jarvis begins producing output-transcription text, any non-empty
  `user_buffer` is logged and cleared.
- Clearing the buffer prevents duplicate logging if the original completion
  path already ran.

## Verification result

The feature was tested through a live Gemini session.

Confirmed results:

- Exactly one `You:` entry was written.
- Exactly one `Jarvis:` entry was written.
- No duplicate user entry appeared.
- The weather tool continued to execute successfully.
- Temporary debug instrumentation was removed after verification.

## Separate observed issue — Transcription accuracy

The displayed input transcription was not fully accurate during testing.

The model still selected the correct weather tool and location, suggesting
that the displayed transcription may not perfectly represent the audio
understanding used by the live model.

This is a separate issue from transcript logging and has not yet been
investigated.

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