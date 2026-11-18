# Hosting

A hiring manager should be able to open a public page, call the API, and see which numbers come from the public UCSD reviews. The pieces that need an account are listed at the end. Nothing in this repository contains a secret, and the code does not invent one.

## What is already public, with no account

The McAuley Lab files are public. `fit-finder-pipeline` downloads them from:

- `https://mcauleylab.ucsd.edu/public_datasets/data/modcloth/modcloth_final_data.json.gz`
- `https://mcauleylab.ucsd.edu/public_datasets/data/renttherunway/renttherunway_final_data.json.gz`

No token. The gzip files stay in `data/raw/`, which is gitignored. Cleaning drops review text and names. The committed model, catalog, and `models/provenance.json` were produced from that table: 275,334 reviews, 192,544 Rent the Runway and 82,790 ModCloth.

The synthetic file `data/fixtures/reviews.csv` is what CI trains on. The pipeline refuses to load it into the hosted database.

Checked on 2026-11-18 by downloading both gzip files and cleaning them in this repo. The row counts, fit counts, shopper count, and item count matched `docs/metrics/data_profile.json`.

## Where it runs

| Piece | Host | Cost | Why this one |
|---|---|---|---|
| API | Render free web service (`render.yaml`) | $0, no credit card | Docker, public https URL, 750 instance hours a month. Sleeps after 15 idle minutes and wakes on the next request, about a minute. Hugging Face Docker Spaces now require a paid plan. Render's free Postgres expires after 30 days, so it is not the database. |
| Review table and demo events | Neon Postgres free plan | $0, no credit card | 1 GB per project, does not expire, scales to zero. The cleaned table fits. Use the **direct** connection string (hostname without `-pooler`) because the loader uses `COPY`. |
| Demo page, learning site, CSV extracts, Power BI limitation page | GitHub Pages | $0 | Already the project's static host. The workflow publishes `academy/site` plus `demo-store`, the extracts, and the Power BI note. |
| Dashboard | Power BI | see the limitation below | Locked. Streamlit and Dash are not substitutes. |

`FIT_FINDER_DATABASE_URL` empty is a real state. The API still serves the committed model and catalog and says `reviews_host: not_configured`. It does not pretend the table is in Neon.

## H&M

Not used on the public API. The Kaggle competition rules limit that dataset to non-commercial purposes and academic research and do not allow redistribution (`DATA ACCESS AND USE: Non-Commercial Purposes & Academic Research`). `transactions_train.csv` is about 31.8 million rows and does not fit the free 1 GB database beside the UCSD table. The comparison stays on the synthetic fixture, which is the CI and offline fallback. A private download remains behind `KAGGLE_USERNAME`, `KAGGLE_KEY`, and `FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD=1`, and that file must not be loaded into the public database.

## Power BI

There is no durable $0 way to give a stranger an interactive Power BI report.

Microsoft's free-license feature list says a free user cannot create a Publish to web embed code and cannot share content with another user. Publish to web also does not support reports that contain report-level DAX measures, which is how these measures are written. Power BI Pro is a paid license, so this project does not use it. Power BI Desktop is a Windows program on the owner's computer.

Closest free path: the CSV extracts are in `analytics/extracts/` and the Pages workflow copies them to `/extracts/` on the site. A hiring manager can download them and open them in Power BI Desktop. The owner can also publish the report to My workspace and look at it there. That view is not shared.

## What a hiring manager can open

The API is live at `https://fit-finder-27yw.onrender.com` on Render's free plan. It reads the Neon table of 275,334 public UCSD reviews. OpenAPI is `https://fit-finder-27yw.onrender.com/docs`.

1. Open `https://neelsrejan.github.io/fit-finder/demo/`. The page calls the API. The first request after a quiet stretch shows "waking the free server (~1 min)" because the free instance sleeps after 15 idle minutes. The extension is optional.
2. Call `GET /health`, `GET /data/profile`, `GET /items?category=dress`, `POST /predict-size`, and `POST /recommend` on `https://fit-finder-27yw.onrender.com`.
3. Load `extension/` unpacked if they want the panel injected. The manifest matches the demo page and localhost. It does not match retailer sites. `https://*.onrender.com/*` is a host permission so the panel can call the API, not a content-script match.
4. Read `/powerbi/` on the site for the dashboard limitation, and download the extracts.

`deploy/public.json` and `extension/config.js` both name `https://fit-finder-27yw.onrender.com`. The offline page at `http://127.0.0.1:8080/` still calls the local API.

## Owner checklist

Do these in order. Stop when a step needs a value you have not created. Do not commit any of the values.

1. **GitHub Pages** (no new account; the repo is already on GitHub).
   - Where: repository Settings → Pages → Build and deployment → GitHub Actions.
   - Workflow: `.github/workflows/pages.yml`, on `main`.
   - URL: `https://neelsrejan.github.io/fit-finder/`.
   - Free: yes. The learning site, the demo page, the extracts, and the Power BI note are static files.

2. **Render** for the API. Done.
   - Live origin: `https://fit-finder-27yw.onrender.com`. Health check path: `/health`.
   - Plan: Free. Do not add a credit card. If the included bandwidth runs out, Render suspends the free service instead of billing.
   - The image sets `FIT_FINDER_ROOT=/app` so model and profile paths are the copied tree, not `site-packages`.
   - `FIT_FINDER_DATABASE_URL` is the Neon direct string, set in the Render dashboard, not in git. `FIT_FINDER_PUBLIC_API_URL` is `https://fit-finder-27yw.onrender.com`.
   - Check: `GET /health` returns `model_loaded: true`, `training_rows: 275334`, and `reviews_host: neon`.

3. **Neon** for the cleaned reviews and demo events.
   - Where: [https://neon.com](https://neon.com) → Free plan. No credit card. Create a project, then copy the **direct** connection string (the host does not contain `-pooler`).
   - Env name: `FIT_FINDER_DATABASE_URL`.
   - Set it in the Render service environment, and export it in the shell where you run the loader. Do not put it in a file that git tracks.
   - Load, from a machine that can reach both UCSD and Neon:

     ```bash
     export FIT_FINDER_DATABASE_URL='postgresql://…'
     fit-finder-pipeline
     ```

   - The command downloads the public gzip files, cleans them, and `COPY`s the table. Review text is not in the table.
   - Check: `GET /data/profile` shows `reviews_host: neon` and `hosted_rows: 275334`.
   - `FIT_FINDER_REQUIRE_HOSTED_STORE=1` makes a missing URL a hard failure. Leave it unset until the URL exists.

4. **Power BI / Microsoft account**, only if you want to look at the report yourself.
   - Where: [https://app.powerbi.com](https://app.powerbi.com) with a free Microsoft account, and Power BI Desktop on Windows, following `analytics/powerbi/BUILD.md`.
   - There is no env var. A free license cannot create a public embed and cannot share the report. Do not buy Pro for this project.
   - The public substitute is the CSV extracts on GitHub Pages, not another dashboard tool.

5. **Kaggle**, only for a private offline H&M download. Not required for the public demo.
   - Where: Kaggle → Account → Create New Token, after accepting the competition rules in a browser.
   - Env: `KAGGLE_USERNAME`, `KAGGLE_KEY`, and `FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD=1`.
   - Do not load that file into Neon and do not point the public API at it. The license is non-commercial and academic research, with no redistribution.

6. **Chrome Web Store**. Not used. The developer registration fee is $5, which is not zero spend. A hiring manager loads `extension/` unpacked, or skips the extension and uses the demo page.
