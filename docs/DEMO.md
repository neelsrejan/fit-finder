# Demo

## What a reader can run

```bash
python -m pip install -e ".[dev]"
fit-finder-api
```

From `demo-store`:

```bash
python -m http.server 8080
```

Open `http://127.0.0.1:8080/`. The page is a fixture: one dress, a size chart, a price, and three colors. It is not a store.

Load `extension/` in Chrome at `chrome://extensions` with Developer mode on, then "Load unpacked". The panel appears on the demo page and calls the API. If the API is down, the panel says so.

`demo-store/fixtures/top.html` is a second saved page with the same contract, used so the parser is not tied to a single file. Open it at `http://127.0.0.1:8080/fixtures/top.html`.

## What this is not

There is no recording of a retailer site. The extension cannot run on one. The storyboard image at `extension/storyboard.gif` is drawn from the panel states. It is not a capture of Chrome, and the README does not call it a user study.
