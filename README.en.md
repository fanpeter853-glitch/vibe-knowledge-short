# vibe-knowledge-short

**English** · [中文](README.md)

A production line for "Vibe Knowledge"-style explainer shorts: near-black night palette, big
Song-style Chinese type, **frame-by-frame code animation**, no voice-over, bilingual subtitles,
and cuts locked to the beat of a BGM you supply.

One film = one abstract claim, performed on screen with a handful of real objects. The viewer reads
one line of subtitle at the bottom while the picture finishes that sentence.

![preview](preview.gif)

*(first 14.5s of the reference film "Entrepreneurship is living with uncertainty")*

This skill covers the **production line only**. It drives the rendering engine from
[`vibe-knowledge-film`](https://github.com/HeyChengC/vibe-knowledge-film) (Canvas + `seek(t)`
frame-accurate, "C Nocturne" look) and adds a fixed spec sheet, portable scripts and a
beat-mapping convention.

## Install

```bash
git clone https://github.com/fanpeter853-glitch/vibe-knowledge-short.git ~/.claude/skills/vibe-knowledge-short
git clone https://github.com/HeyChengC/vibe-knowledge-film.git ~/.claude/skills/vibe-knowledge-film   # engine
python ~/.claude/skills/vibe-knowledge-short/scripts/setup.py                                        # fonts + self-check
```

Any agent that works by reading `SKILL.md` (Claude Code, Codex, Cursor, your own agent) just needs
this folder in its skills directory. Zip-only clients can import the zipped folder — the engine and
fonts are not required in the archive, `setup.py` fetches them.

**Apps with no custom-skill support (e.g. Meta Muse)**: use [`MUSE-paste.md`](MUSE-paste.md) — paste
the instructions into a chat. It will handle design only (storyboard, subtitle table, beat sheet);
rendering stays on a machine that can run the engine.

Dependencies: Python 3.10+, `playwright` (uses local Chrome, falls back to bundled chromium),
`numpy`, `scipy`, `Pillow`, `ffmpeg`.

## What a run looks like

```
user : make a 60s short on "why is the sky blue", here is my BGM
agent: read SKILL.md -> fill storyboard -> scaffold project -> write film.js
       -> render in 4 segments -> mix BGM -> film + cover frame
```

A human supplies three things: **topic**, **BGM**, **length preference**. Everything else — objects,
storyboard, subtitles, beat cuts, citations — is the production line's job.

## Layout

```
SKILL.md                        production rules (the agent reads this)
scripts/
  setup.py                      resolves engine / downloads fonts / finds ffmpeg / checks playwright
  _env.py                       cross-platform path resolution (VKF_ENGINE, FFMPEG overrides)
  render_range.py               render a frame range into one segment (run 4 in parallel)
  assemble.py                   concat segments + mix BGM + extract cover
references/
  pitfalls.md                   earned lessons (fonts, ffmpeg, temp dirs, subtitle collisions)
  storyboard-template.md        storyboard / subtitle table template
MUSE-paste.md                   paste-ready instructions for Meta Muse
```

## License

MIT. Engine and fonts follow their upstream licenses (engine MIT; fonts SIL OFL 1.1, fetched from
Google Fonts at setup time and never committed).
