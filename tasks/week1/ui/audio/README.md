# Lear Audio Architecture — approved boundary before assets

No sound assets are currently shipped. This document defines the safe architecture required before adding any audio.

## Rules

- Audio is opt-in and muted by default until the user enables it.
- Every effect must be tied to an intentional product event: alert, action completion, connection state or notification—not decoration.
- Audio files must have verified licenses recorded in an asset manifest.
- Effects are lazy-loaded by event category; no global preload of a sound library.
- Use compressed, short files with a strict total budget agreed before implementation.
- Respect browser autoplay policy; playback requires a user gesture.
- Provide global mute, per-category volume and a test button in Settings.
- Respect `prefers-reduced-motion` and an independent reduced-audio preference.
- Never play audio for repeated polling, typing, hover or every animation frame.
- Tests must verify mute behavior, failed playback recovery and no network request before opt-in.

## Proposed implementation boundary

`desktop/src/audio/AudioProvider.tsx` will own user preference and an `AudioEvent` map. `desktop/src/audio/loadSound.ts` will dynamically import one approved asset at a time. Components dispatch semantic events rather than importing files directly. This keeps audio replaceable, testable and outside the dashboard/chat rendering path.

## Current status

Architecture documented; assets intentionally not added. This keeps the repository within its performance, licensing, accessibility and maintainability limits.
