---
name: auto-video-editor-windows
description: Use when a Windows user points to a local video and wants it edited, cleaned, transcribed, or cut into livestream highlights.
---

# Auto video editor for Windows

Use local HotClip and FFmpeg to create reviewable video edits on Windows. Install this standard Agent Skill into the current agent with that agent's native skill installer. Requirements for video editing: Windows 10 or later, internet access, and several GB of free disk space. When the user asks to run this skill on Windows, the active agent installs Git, Node.js LTS, FFmpeg, HotClip and HotClip's speech model using the available Windows package manager. No repository bootstrap script or Ollama is required. Restart the agent after installation if needed.

## Workflow

1. Probe the source with `ffprobe`: duration, frame size, and audio/video streams. Preserve the source and create a new sibling output folder `成品_自动精剪_YYYY-MM-DD`; use a numeric suffix if it already exists.
2. For videos over five minutes, choose the highlight count from the transcript: normally 1–2 for under 15 minutes, 2–4 for 15–60 minutes, and 3–5 for over 60 minutes. These are ceilings, not quotas; return fewer when there are not enough distinct, complete, useful moments. Avoid repetitive topics. For shorter finished clips, clean the whole clip conservatively. If the user asks to retain the full recording, do not extract highlights.
3. Transcribe locally with HotClip's word-timestamped ASR. Review the transcript against the audio before using it for cuts or captions. HotClip's automatic `highlights` and `clip` commands require a configured LLM endpoint; in this no-LLM workflow, the active assistant selects moments from the transcript and renders them with FFmpeg. Do not upload footage or transcript.
4. **Remove clear filler words by default.** Review isolated hesitation sounds such as `嗯`, `呃`, `额`, `唔`, `诶`, `um`, `uh`, and obvious immediate stutter repeats. Check each candidate in the audio before cutting. Treat `啊`, `这/这个`, `那个`, `就是`, and `然后` as context-dependent: remove them only when they are plainly non-semantic hesitation or repeated scaffolding, and the sentence remains natural. Keep meaningful emphasis, references, transitions, and any uncertain word. Never use a blind text replacement across the transcript. Cut only complete word spans with a small natural audio boundary; preserve breaths and room tone unless they are clearly unwanted.
5. **Produce subtitles for every spoken clip by default.** Create accurate Chinese captions from the reviewed transcript, remove words that were actually cut, and retime all cues against the edited output timeline. Keep readable short lines (normally one or two lines), natural punctuation, and safe margins. Deliver both a hard-subtitled MP4 and a matching SRT sidecar. If the user requests no subtitles, omit both only after following that request. Never present an unburned caption plan as a subtitled export.
6. Set highlight and filler-cut boundaries on complete words and sentences. Check the transcript and audio around every start and end; never rely only on `midWordCuts: 0`. Assemble the retained intervals into one edit and keep an edit decision list. For a source time `t` inside a retained interval `[source_start, source_end]`, calculate its output time as `t - source_start + cumulative_duration_of_prior_retained_intervals`; omit words removed by filler cuts. Build the SRT on this output timeline, use the same interval map for audio/video concatenation, then burn the SRT into the rendered MP4 with FFmpeg’s subtitle filter.
7. Preserve the source's main picture and graphics. For the recurring blue livestream banner, replace only its old episode title with a concise, faithful title from the transcript; keep the permanent masthead and decorative artwork. Place burned captions near the bottom with about 40 px clearance at 1080×1920. Inspect a rendered frame for readable, unclipped text.
8. Preserve continuous audio by default except for verified filler words, unwanted silence, or user-requested edits. Treat VAD silence as a candidate: if a proposed cut overlaps an ASR word, inspect the audio and preserve speech. For visual overlays, stream-copy the rendered audio where possible and compare its audio packet hash with the pre-overlay render.
9. Verify each export with `ffprobe`, full FFmpeg decode, audio/video stream checks, black-frame scan, silence scan, duration, subtitle presence/synchronization, and opening/ending word checks. Listen to the rendered start, middle, and end. Map long silences back to the source and report whether they were in the recording or introduced by editing. Surface unresolved QA warnings and report only checks actually performed.
10. Do not publish or upload. Deliver absolute paths to each MP4 and SRT, duration, output folder, and a Markdown edit report with QA links.

## Commands

When HotClip is installed, it is placed in `%LOCALAPPDATA%\HotClip\app`. In PowerShell:

```powershell
Set-Location "$env:LOCALAPPDATA\HotClip\app"
pnpm cli transcribe 'C:\Videos\recording.mp4' --json > 'C:\Videos\transcript.json'
```

Transcription runs locally. Choose a count within the duration-based ceilings according to distinct, self-contained moments in the transcript; never fill the maximum just because it exists. Always render spoken captions and a matching SRT unless the user asks to omit them. Remove only individually verified filler-word spans, then retime subtitle cues to the output timeline. Render only after checking transcript boundaries and audio safety.
