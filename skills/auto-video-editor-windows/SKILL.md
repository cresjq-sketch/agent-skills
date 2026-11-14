---
name: auto-video-editor-windows
description: Use when a Windows user points to a local video and wants it edited, cleaned, transcribed, or cut into livestream highlights.
---

# Auto video editor for Windows

Use local HotClip and FFmpeg to create reviewable video edits on Windows. Install this standard Agent Skill into the current agent with that agent's native skill installer. Requirements for video editing: Windows 10 or later, internet access, and several GB of free disk space. When the user asks to run this skill on Windows, the active agent installs Git, Node.js LTS, FFmpeg, HotClip and HotClip's speech model using the available Windows package manager. No repository bootstrap script or Ollama is required. Restart the agent after installation if needed.

## Workflow

1. Probe the source with `ffprobe`: duration, frame size, audio/video streams. Preserve the source and create a new sibling output folder `成品_自动精剪_YYYY-MM-DD`; use a numeric suffix if it already exists.
2. For videos over five minutes, choose the highlight count from the transcript: normally 1–2 for under 15 minutes, 2–4 for 15–60 minutes, and 3–5 for over 60 minutes. These are ceilings, not quotas; return fewer when there are not enough distinct, complete, useful moments. Avoid repetitive topics. For shorter finished clips, clean the whole clip conservatively. If the user asks to retain the full recording, do not extract highlights.
3. Use HotClip's local, word-timestamped transcription. The active assistant reviews the transcript and selects the moments. HotClip's automatic `highlights` and `clip` commands require a separately configured LLM endpoint and are not used by this no-LLM bundle. Do not upload footage or transcript.
4. Set boundaries on complete words and sentences. Check the transcript around each start and end; never rely only on `midWordCuts: 0`.
5. Treat VAD silence as a candidate. Do not cut a span that overlaps an ASR word without inspecting the audio. If the user reports missing speech, pause jump cuts and filler removal, map the output interval to source time (use the EDL for multi-piece edits), and check whether the same silence exists in the original.
6. Preserve the source's main picture and graphics. For the recurring blue livestream banner, replace only its old episode title with a concise, faithful title from the transcript; keep the permanent masthead and decorative artwork. Burn one centered spoken-caption layer near the bottom with about 40 px clearance at 1080×1920. Inspect a rendered frame for readable, unclipped text.
7. Keep audio continuous by default. Enable jump cuts or filler removal only for verified intervals. For visual-overlay edits, stream-copy the rendered audio where possible and compare its audio packet hash with the pre-overlay render.
8. Verify each export with `ffprobe`, full FFmpeg decode, audio/video stream checks, black-frame scan, silence scan, duration, and opening/ending word checks. Map each long silence back to the source and report whether it was present in the recording or introduced by editing. Surface unresolved QA warnings and report only steps actually performed.
9. Do not publish or upload. Deliver absolute paths to each MP4, duration, output folder, and a Markdown edit report with QA links.

## Commands

When HotClip is installed, it is placed in `%LOCALAPPDATA%\HotClip\app`. In PowerShell:

```powershell
Set-Location "$env:LOCALAPPDATA\HotClip\app"
pnpm cli transcribe 'C:\Videos\recording.mp4' --json > 'C:\Videos\transcript.json'
```

Transcription runs locally. Choose a count within the duration-based ceilings according to distinct, self-contained moments in the transcript; never fill the maximum just because it exists. Render only after checking transcript boundaries and audio safety.
