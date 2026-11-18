# fit-finder extension

Unpacked Manifest V3 extension for the demo page. Chrome Web Store registration costs $5, so the extension is not published there.

The page a hiring manager opens is `https://neelsrejan.github.io/fit-finder/demo/` once GitHub Pages is enabled. That page calls the API without this extension. Load the extension only if you want the panel injected.

1. Optional offline API: `fit-finder-api` (listens on `127.0.0.1:8000` when `PORT` is unset).
2. Optional offline page: from `demo-store`, `python -m http.server 8080`.
3. Chrome → Extensions → Developer mode → Load unpacked → this folder.
4. Open the hosted demo, or `http://127.0.0.1:8080/` for the offline page.

The content script matches `http://127.0.0.1/*`, `http://localhost/*`, and `https://neelsrejan.github.io/fit-finder/*`. It does not match retailer hosts. `https://*.onrender.com/*` is a host permission for the API call.

`extension/config.js` holds the public API origin. It stays empty until the Render service exists. The popup can store an origin override in this browser. Neither file holds a secret.

The page contract, shared with `src/fit_finder/pageparse.py`:

- `article.product` with `data-product-id`, `data-category`, `data-price`, `data-colors`
- `table.size-chart tr[data-size]`
- `select#size-select`

`storyboard.gif` is a drawn sequence of the panel, for the README. It is not a screen capture.
