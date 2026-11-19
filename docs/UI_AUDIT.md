# UI audit

Reviewed 2026-11-19, before the guided walkthrough. The question was whether a first-time hiring manager is led through the product, or handed a set of controls and left to invent the order.

Reference for the visual system, not for the layout: [invalid-agent](https://invalid-agent-lwycv4pt4vd4emwhuiqde3.streamlit.app/) (`app/streamlit_app.py` in [neelsrejan/invalid-agent](https://github.com/neelsrejan/invalid-agent)). That app is a light Streamlit page: paper background `#F7F5F2`, navy banner `#0B3A5B`, secondary panels `#E7EEF2`, ink `#1C2830`, a metric row, one or two Plotly charts, a dataframe, captions, and suggested-question buttons. Its information architecture is a dashboard (sidebar scenario, week slider, rules toggle, five metrics, two charts, a strata select, six tabs). fit-finder should take the visual system. It should not take the knob layout.

## What is live

| Surface | URL | What a visitor actually gets |
|---|---|---|
| Fixture store | https://neelsrejan.github.io/fit-finder/demo/ | One product page. |
| Learning site | https://neelsrejan.github.io/fit-finder/ | Ten-session course with a sidebar. |
| API console | https://fit-finder-27yw.onrender.com/docs | Swagger UI. Title in the live HTML: "fit-finder - Swagger UI". |
| Power BI note | https://neelsrejan.github.io/fit-finder/powerbi/ | A short page that says the report cannot be published. |
| API health | https://fit-finder-27yw.onrender.com/health | Checked the same day. HTTP 200 after a 34 second cold start. `reviews_host` is `neon`, `hosted_rows` is 275334, `training_rows` is 275334, model and catalog loaded. |

The extension is a fifth surface. It is not on a public URL. A visitor loads `extension/` unpacked. The manifest matches the fixture page and localhost only.

## Current layout

### Fixture store

Navy header, warm page, one disclaimer, one dress, a size `<select>`, and a size chart. `demo-store/panel.js` then posts `/predict-size` and `/recommend` by itself and writes a suggested size plus three item ids. There is no step indicator, no chart, no held-out number, and no simulation label on the page shell.

The size `<select>` does not resubmit. The script reads the `selected` attribute once, at load. Changing the dropdown does not ask the model again.

This is not a dashboard. It is also not a tour. The page runs one call and stops. A visitor who wanted the model card, the experiment, or Power BI has to already know those live somewhere else.

### Learning site

Left sidebar of ten sessions in three sprints, a progress ring, and a quiz lock. Home offers three equal cards: the repository, the Power BI build guide, and the fixture page. The local run block starts `fit-finder-api`, then stops. Nothing on the home page says "do this, then this."

The sidebar is course navigation. It is the right shape for someone learning the code session by session. It is the wrong shape for a hiring manager who opened the project to see a size decision.

### Swagger

A control panel. Routes are listed (`/health`, `/data/profile`, `/items`, `/predict-size`, `/recommend`, `/events`, `/limits`) and each one has a try-it-out form. The order is not in the UI. A visitor who does not already know the story has to guess which route is the point.

The data behind it is the real public table. The console does not say that in a sentence a non-API reader will finish.

### Power BI page

One column of prose. It correctly says this is not a substitute dashboard, and it points at the CSV extracts. There is no chart of the simulated experiment, so the only public view of that result is a markdown file in the repo.

### How a first visit actually feels

The portfolio is four public surfaces plus an unpacked extension. None of them is "Step N of M." The fixture auto-runs. The learning site and Swagger ask the visitor to pick. The Power BI page is a dead end with no picture.

Things a first-time visitor has to figure out alone:

- Which URL is the demo. Home presents three cards of equal weight.
- Whether the model has already run, and on which size. The panel fills in after a wait that looks like a hang. The cold start measured here was 34 seconds, and the free instance sleeps after 15 idle minutes.
- Whether changing the size dropdown does anything. It does not.
- What an item id is. The panel prints ids and a fit rate, not a reason to look at that row.
- Which numbers are from the public reviews and which are simulated. That split is in `README.md` and `docs/EVAL_REPORT.md`, not on the page that shows the size.
- That the neighbor-size suggestion lost to the most-common-fit-size rule on the test split. That sentence is in the model card. The panel still presents the suggested size as the answer.
- That the Power BI page is a license limit, not a broken embed.
- That the extension is optional and cannot run on a retailer site.

## Verdict

Control-panel and course-nav layout, plus one auto-running fixture. Not a guided flow. The visitor supplies the order.

## Redesign

A Streamlit walkthrough on Community Cloud, deployed from `main`, main file `streamlit_app.py`. Same theme tokens as invalid-agent. The Render API, the Neon table, the fixture page, the extension, and the Power BI extracts stay. Streamlit is the front door. It is not a replacement for the Power BI dashboard. Synthetic reviews are the CI fallback only. `auto` tries the API and, if the free server does not answer, uses the committed public-review artifact. It does not silently switch to the synthetic fixture.

Eight steps. Each one says what fit-finder is doing, why, and what to look at, and shows that step's chart or table only. Suggested prompts are buttons. Next and Back stay in order. A step list in the sidebar jumps. Free explore is a toggle, and it is also the forward button on the last step.

1. **The question.** The Rivet dress, size 8, and the line between public reviews and simulated shoppers. Prompts for the dress, a gown in size 4, or a top in size 12.
2. **The reviews.** Row count, shoppers, items, and a bar of fit / small / large. When the API is awake the Neon row count is on this step.
3. **The size she is considering.** The request body. Price and color are not in it. Prompts score that size, or a size two steps away, and the next step actually rescores.
4. **The size call.** Class, confidence, ordered size, suggested size, and the three probabilities.
5. **Similar items.** Fit-rate bars and the ranked table. The price note stays labeled as an illustrative band.
6. **Was the model any good.** Held-out log loss for majority, logistic, and LightGBM, then the directional loss in a caption.
7. **What is simulated.** The two-arm return chart, marked simulated, plus the H&M fixture line and the Power BI limit. Links to the existing note and the extracts.
8. **The recommendation.** The size to show her, the first similar item, and the held-out number that is safe to repeat. Then free explore: category, size, height, score, health, limits, and, only on the live API, one demo event.

Free explore keeps the same service. It does not put those knobs on the earlier steps.

## What does not change

- Neon holds the cleaned public UCSD table. The synthetic fixture is still refused as a hosted load.
- The Render service stays the API. The walkthrough calls it. The Neon URL stays in the Render environment, not in the Streamlit app and not in git.
- The fixture page and the extension stay, so the parser test and the manifest boundary stay.
- Power BI stays the analytics dashboard. The free license still cannot publish it. The walkthrough links to the note and shows the one simulated chart the extracts already contain.
