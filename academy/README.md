# fit-finder learning site

Static pages for sessions 1 through 10. Quizzes, progress, and videos have no backend and no paid service.

Speech is edge-tts only, voice `en-US-AndrewNeural`. The renderer will not fall back to another engine. Each clip opens with an architecture frame, then a line walkthrough of the file on `main`.

Quizzes are about boundaries and tradeoffs. They do not ask for syntax or line numbers. Pass at 80% (7 of 8) to unlock the next session. Progress stays in `localStorage`. Export copies a checksummed code (`FF1.…`) you can paste on another computer.

## Study

The Pages workflow (`.github/workflows/pages.yml`) uploads `academy/site`, including the walkthrough MP4s. It does not re-render them. GitHub-hosted runners do not ship ffmpeg, and the speech service is not reliable there. Re-render locally when the narration changes, commit the new MP4s under `academy/site/videos/`, and let the workflow publish them.

The URL, once Pages is set to GitHub Actions, is `https://neelsrejan.github.io/fit-finder/`.

If that setting is still off: Settings → Pages → Build and deployment → GitHub Actions. The first deploy fails with a Pages 404 until that source is selected.

Locally, after a render:

```bash
pip install -r academy/requirements.txt
python3 academy/scripts/render_all.py
python3 academy/scripts/build_site.py
python3 -m http.server -d academy/site 8765
```

The MP4s are committed under `academy/site/videos/`. Clip durations live in `academy/content/durations.json`. CI runs `build_site.py` and fails if `academy/site/` HTML or `academy/content/QUIZ_ANSWERS.md` drift. The video files are not rewritten by that script.

`academy/content/bank.py` is the authoring copy. The build shuffles the four choices and writes a salted SHA-256 of the published letter. That hash is a self-study speed bump, not protection.

The code on screen is `main`, not a historical tag. This repo was built as one tree. The invalid-agent Academy uses session tags because that project grew one session at a time. The video method is the same.
