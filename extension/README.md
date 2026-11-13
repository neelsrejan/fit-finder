# fit-finder extension

Unpacked Manifest V3 extension for the demo store.

1. Run the API: `fit-finder-api`.
2. Serve `demo-store` on port 8080.
3. Chrome → Extensions → Developer mode → Load unpacked → this folder.
4. Open `http://127.0.0.1:8080/`.

The content script matches `http://127.0.0.1/*` and `http://localhost/*` only.

The page contract, shared with `src/fit_finder/pageparse.py`:

- `article.product` with `data-product-id`, `data-category`, `data-price`, `data-colors`
- `table.size-chart tr[data-size]`
- `select#size-select`

`storyboard.gif` is a drawn sequence of the panel, for the README. It is not a screen capture.
