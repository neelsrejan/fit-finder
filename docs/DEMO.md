# Demo

## What a reader can open

The hosted demo is `https://neelsrejan.github.io/fit-finder/demo/` after GitHub Pages is enabled and `deploy/public.json` has the Render origin. The page is a fixture: one dress, a size chart, a price, and three colors. It is not a store. The suggestion comes from the API. If the API URL is still empty, the page says so and does not invent a size.

The API docs, once Render is connected, are `https://<service>.onrender.com/docs`. `GET /health` reports whether the committed public-review model is loaded and whether Neon is configured.

Offline, on a laptop:

```bash
python -m pip install -e ".[dev]"
fit-finder-api
```

From `demo-store`:

```bash
python -m http.server 8080
```

Open `http://127.0.0.1:8080/`. The page calls `http://127.0.0.1:8000` only when it is itself served from localhost.

Load `extension/` in Chrome at `chrome://extensions` with Developer mode on, then "Load unpacked", if you want the panel injected. If the API is down, the panel says which origin it tried.

`demo-store/fixtures/top.html` is a second saved page with the same contract, used so the parser is not tied to a single file. Open it at `http://127.0.0.1:8080/fixtures/top.html`.

## What this is not

There is no recording of a retailer site. The extension cannot run on one. The storyboard image at `extension/storyboard.gif` is drawn from the panel states. It is not a capture of Chrome, and the README does not call it a user study.
