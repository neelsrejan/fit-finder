#!/usr/bin/env python3
"""Build the static learning-site pages. Quiz keys are salted hashes, not letters."""

from __future__ import annotations

import base64
import hashlib
import html
import json
import random
import sys
from collections import Counter
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[2]
ACADEMY = ROOT / "academy"
SITE = ACADEMY / "site"
sys.path.insert(0, str(ACADEMY))
sys.path.insert(0, str(ACADEMY / "content"))

from bank import QUIZZES  # noqa: E402
from course import SESSIONS  # noqa: E402
from quiz_checks import assert_guessers, assert_uniform_options  # noqa: E402

REPO = "https://github.com/neelsrejan/fit-finder"
MD = markdown.Markdown(extensions=["extra", "sane_lists"], output_format="html5")
SPRINTS = ((1, (1, 2, 3)), (2, (4, 5, 6, 7)), (3, (8, 9, 10)))


def md(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def salt_for(session: int, qid: str) -> str:
    return hashlib.sha256(f"ff-quiz|{session}|{qid}|v1".encode()).hexdigest()[:16]


def answer_hash(salt: str, choice: str) -> str:
    return hashlib.sha256(f"{salt}|{choice}".encode()).hexdigest()


def b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def load_clips(session: int) -> list[dict]:
    folder = ACADEMY / "narration" / f"session-{session}"
    clips = []
    for script in sorted(folder.glob("*.yaml")):
        spec = yaml.safe_load(script.read_text())
        path = str(spec["file"]).replace("\\", "/")
        overview = spec.get("overview") or {}
        clips.append(
            {
                "stem": script.stem,
                "title": spec.get("title") or script.stem,
                "path": path,
                "seconds": clip_seconds(session, script.stem),
                "src": f"videos/session-{session}/{script.stem}.mp4",
                "blob": f"{REPO}/blob/main/{path}",
                "overview": " ".join(str(overview.get("say") or "").split()),
            }
        )
    if not clips:
        raise SystemExit(f"no narration yaml for session {session}")
    return clips


def clip_seconds(session: int, stem: str):
    manifest = ACADEMY / "content" / "durations.json"
    key = f"session-{session}/{stem}"
    if manifest.exists():
        data = json.loads(manifest.read_text())
        if key in data:
            return data[key]
    return None


def clock(seconds) -> str:
    if seconds is None:
        return "duration after render"
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def published_choices(q: dict, salt: str) -> tuple[dict[str, str], str]:
    correct_text = q["choices"][q["correct"]]
    texts = [q["choices"][key] for key in "abcd"]
    random.Random(salt).shuffle(texts)
    labeled = {letter: texts[i] for i, letter in enumerate("abcd")}
    published = next(letter for letter, text in labeled.items() if text == correct_text)
    return labeled, published


def quiz_payload() -> dict:
    payload = {}
    for session, questions in QUIZZES.items():
        if len(questions) != 8:
            raise SystemExit(f"session {session} has {len(questions)} questions")
        built = []
        for i, q in enumerate(questions, 1):
            qid = f"s{session}q{i}"
            salt = salt_for(session, qid)
            labeled, published = published_choices(q, salt)
            built.append(
                {
                    "id": qid,
                    "prompt": q["prompt"],
                    "choices": [{"id": key, "text": labeled[key]} for key in "abcd"],
                    "salt": salt,
                    "answerHash": answer_hash(salt, published),
                    "explain": b64(q["why"]),
                }
            )
        payload[str(session)] = {"passMark": 0.8, "questions": built}
    return payload


def graded_items(payload: dict) -> list[dict]:
    items = []
    for session, pack in payload.items():
        for question in pack["questions"]:
            winner = None
            for choice in question["choices"]:
                if answer_hash(question["salt"], choice["id"]) == question["answerHash"]:
                    if winner is not None:
                        raise SystemExit(f"{question['id']} hashes to two letters")
                    winner = choice
            if winner is None:
                raise SystemExit(f"{question['id']} hash matches no choice")
            items.append(
                {
                    "session": int(session),
                    "prompt": question["prompt"],
                    "choices": question["choices"],
                    "correct": winner["id"],
                }
            )
    return items


def nav(active: int) -> str:
    by_id = {s["id"]: s for s in SESSIONS}
    parts = [
        '<a class="brand" href="index.html"><div class="mark">ff</div><div><strong>fit-finder</strong><span>Learning site</span></div></a>',
        f'<a class="item{" active" if active == 0 else ""}" href="index.html">Home</a>',
    ]
    for sprint, ids in SPRINTS:
        parts.append(f'<div class="week">Sprint {sprint}</div>')
        for n in ids:
            title = html.escape(by_id[n]["title"])
            active_cls = " active" if n == active else ""
            parts.append(
                f'<a class="item{active_cls}" data-session="{n}" href="session-{n}.html">'
                f'<i class="dot"></i>S{n} · {title}</a>'
            )
    parts.append('<div class="nav-foot" id="nav-progress">Progress stays in this browser</div>')
    return "\n".join(parts)


def page(title: str, body: str, *, session: int, page_name: str) -> str:
    lock = ""
    if session > 1:
        lock = f"""
<script>
(function () {{
  var session = {session};
  var ok = false;
  try {{
    var raw = localStorage.getItem("ff-academy-progress-v1");
    var data = raw ? JSON.parse(raw) : null;
    var prev = data && data.sessions && data.sessions[String(session - 1)];
    ok = !!(prev && prev.passed);
  }} catch (e) {{ ok = false; }}
  if (!ok) document.documentElement.classList.add("is-locked");
}})();
</script>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="css/academy.css">
{lock}
</head>
<body data-page="{page_name}" data-session="{session}">
<div class="app">
<aside class="nav">
{nav(session)}
</aside>
<main class="main">
{body}
</main>
</div>
<script src="js/site-config.js"></script>
<script src="js/quiz-data.js"></script>
<script src="js/academy.js"></script>
</body>
</html>
"""


def home_body() -> str:
    cards = []
    for s in SESSIONS:
        cards.append(
            f"""<a class="session-card" data-session="{s['id']}" href="session-{s['id']}.html">
<div class="num">{s['id']:02d}</div>
<div><h3>{html.escape(s['title'])}</h3>
<div class="meta">Sprint {s['sprint']} · {html.escape(s['minutes'])} min · {html.escape(s['artifact'])}</div></div>
<div class="pill">Open</div>
</a>"""
        )
    return f"""
<p class="kicker">Size and fit · ten sessions · one tree on main</p>
<h1>Learn fit-finder, session by session.</h1>
<p class="lede">A portfolio prototype for apparel fit, narrated against the code that builds it. Held-out fit metrics come from the public UCSD reviews. Shopper traffic in the project is simulated. Quizzes ask why the boundaries exist.</p>
<div class="progress-row">
  <div class="ring" data-progress style="--p:0"><span id="ring-label">0/10</span></div>
  <div>
    <strong id="progress-label">0 of 10 sessions passed</strong>
    <div class="bar" data-progress style="--p:0"><i></i></div>
    <p class="note" id="progress-detail">Pass a quiz at 80% or better to open the next session. Retries are unlimited.</p>
    <p class="note" id="lock-note"></p>
  </div>
</div>
<div class="cards">
  <a class="link-card" id="link-github" href="{REPO}"><div class="label">Repository</div><strong>GitHub</strong><p>neelsrejan/fit-finder. The code on screen is main.</p></a>
  <a class="link-card" href="{REPO}/blob/main/analytics/powerbi/BUILD.md"><div class="label">Dashboard</div><strong>Power BI guide</strong><p>Extracts and DAX are in the repo. The .pbix is built on Windows.</p></a>
  <a class="link-card" href="{REPO}/blob/main/docs/DEMO.md"><div class="label">Demo</div><strong>Local API and demo store</strong><p>The extension does not run on retailer sites.</p></a>
</div>
<h2>How to run it locally</h2>
<div class="panel">
<pre>python -m pip install -e ".[dev]"
python -m pytest
fit-finder-api</pre>
<p class="note">Practice notes stay in your own scratch file. Do not widen the extension manifest.</p>
</div>
<h2>Sessions</h2>
<div class="session-grid">
{''.join(cards)}
</div>
<h2>Move progress between computers</h2>
<div class="panel">
<p>Quiz scores live in this browser's localStorage. Export a code, and paste it on the other machine. The code is a checksummed copy of your scores, not an account.</p>
<div class="row">
  <button type="button" id="export-btn">Export progress</button>
  <button type="button" class="secondary" id="reset-btn">Clear this browser</button>
</div>
<textarea id="export-code" rows="3" readonly placeholder="Your code appears here"></textarea>
<label for="import-code">Paste a code from your other computer</label>
<textarea id="import-code" rows="3" placeholder="FF1...."></textarea>
<div class="row"><button type="button" id="import-btn">Import progress</button></div>
<p class="note" id="transfer-msg"></p>
</div>
"""


def session_body(session: dict, clips: list[dict]) -> str:
    n = session["id"]
    reads = "".join(f"<li>{html.escape(item)}</li>" for item in session["read"])
    clip_html = []
    for i, clip in enumerate(clips, 1):
        overview = (
            f'<div class="panel"><p><strong>Architecture.</strong> {html.escape(clip["overview"])}</p></div>'
            if clip["overview"]
            else ""
        )
        clip_html.append(
            f"""<article class="clip">
<h3>{i}. {html.escape(clip['title'])}</h3>
{overview}
<video controls preload="metadata" src="{html.escape(clip['src'])}">
<a href="{html.escape(clip['src'])}">Download clip {i}</a>
</video>
<p class="meta">{clock(clip['seconds'])} · Andrew · <a href="{html.escape(clip['blob'])}">{html.escape(clip['path'])}</a> on <code>main</code></p>
</article>"""
        )
    files = []
    seen = set()
    for clip in clips:
        if clip["path"] in seen:
            continue
        seen.add(clip["path"])
        files.append(f'<li><a href="{html.escape(clip["blob"])}"><code>{html.escape(clip["path"])}</code></a></li>')
    return f"""
<p class="kicker">Sprint {session['sprint']} · Session {n}</p>
<h1>{html.escape(session['title'])}</h1>
<p class="lede">{html.escape(session['blurb'])}</p>
<p class="note">About {html.escape(session['minutes'])} minutes · artifact: {html.escape(session['artifact'])}</p>
<div class="lock-screen">
  <div class="panel">
    <h2>This session is locked</h2>
    <p>Pass Session {n - 1} at 80% or better to open the videos and this quiz. Retries on the earlier quiz are unlimited. If you already passed it on another computer, import that progress code from the home page.</p>
    <p><a class="button" href="session-{n - 1}.html">Go to Session {n - 1}</a> <a class="button secondary" href="index.html">Home</a></p>
  </div>
</div>
<div class="lesson">
<h2>Read first</h2>
<ul>{reads}</ul>
<h2>Watch in this order</h2>
<p class="note">Each clip opens with what the file is responsible for, then walks the lines. The line numbers match <code>main</code>.</p>
{''.join(clip_html)}
<h2>How this session connects</h2>
<div class="prose">{md(session['trace'])}</div>
<h2>Code on main</h2>
<ul>{''.join(files)}</ul>
<h2>Practice</h2>
<div class="prose">{md(session['practice'])}</div>
<h2>Quiz</h2>
<p class="note">Eight questions. 80% to pass, which means 7 of 8. The questions are about boundaries and tradeoffs. Explanations show after you submit. The salted hash is a self-study speed bump, not protection.</p>
<div id="quiz"></div>
</div>
"""


def write_answer_key(payload: dict) -> None:
    lines = [
        "# Learning-site quiz letters",
        "",
        "These are the letters after `build_site.py` shuffles each question.",
        "The salted hash on the page is a self-study speed bump, not protection.",
        "Reading this file, or trying all four choices, bypasses it.",
        "",
    ]
    for session in range(1, 11):
        lines.append(f"## Session {session}")
        lines.append("")
        for index, question in enumerate(payload[str(session)]["questions"], 1):
            winner = next(
                choice
                for choice in question["choices"]
                if answer_hash(question["salt"], choice["id"]) == question["answerHash"]
            )
            lines.append(f"{index}. **{winner['id'].upper()}.** {winner['text']}")
            lines.append("")
    (ACADEMY / "content" / "QUIZ_ANSWERS.md").write_text("\n".join(lines))


def main() -> None:
    if len(QUIZZES) != 10:
        raise SystemExit("expected 10 quizzes")
    payload = quiz_payload()
    blob = json.dumps(payload, ensure_ascii=False, indent=2)
    items = graded_items(payload)
    assert_uniform_options(items)
    expected = assert_guessers(items)
    letters: Counter = Counter(item["correct"] for item in items)
    n = len(items)
    for letter, count in sorted(letters.items()):
        if count / n > 0.40:
            raise SystemExit(f"letter {letter} is {count}/{n} answers, over 40%")
        print(f"letter {letter}: {count}/{n}")
    for name, by_session in expected.items():
        bits = " ".join(f"s{session}={by_session[session]:.1%}" for session in range(1, 11))
        print(f"guesser {name}: {bits}")
    write_answer_key(payload)
    (SITE / "js").mkdir(parents=True, exist_ok=True)
    (SITE / "js" / "quiz-data.js").write_text("window.QUIZZES = " + blob + ";\n")
    (SITE / "index.html").write_text(page("fit-finder learning site", home_body(), session=0, page_name="home"))
    (SITE / ".nojekyll").write_text("")
    for session in SESSIONS:
        clips = load_clips(session["id"])
        body = session_body(session, clips)
        (SITE / f"session-{session['id']}.html").write_text(
            page(f"Session {session['id']} · {session['title']}", body, session=session["id"], page_name="session")
        )
        print(f"session {session['id']}: {len(clips)} clips")
    print("wrote", SITE)


if __name__ == "__main__":
    main()
