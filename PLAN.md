# fit-finder: Build Plan (approved 2026-11-11)

ML project, not an agent. Clothing size prediction and recommendations, a Chrome extension, FastAPI, and a Power BI dashboard. Ten sessions, three sprints. Public repo `fit-finder`.

Learning site: one page per session, line-by-line walkthrough videos, a short architectural overview before each code block, and quizzes that ask about architecture and design rationale only.

Data: UCSD Rent the Runway and ModCloth fit reviews, free and public. H&M Personalized Fashion Recommendations on Kaggle is blocked on a Kaggle account and API key.

Honesty: shopper traffic, clicks, returns, and A/B results are simulated and labeled. Model metrics are from a held-out test split of the UCSD reviews.

## Sprint 1: data and model

- S1 PRD, roadmap, backlog, repo skeleton, CI, DATA_LICENSES. Deliverable: tests green, README, backlog.
- S2 Data layer: download and clean RTR and ModCloth, normalize sizes, features for measurements, past sizes, item, and category, Parquet store, data tests. Deliverable: clean dataset and a data card.
- S3 Size model: most-common-class baseline versus scikit-learn versus LightGBM. Fit classes are small, fit, and large. Calibrated confidence. Per-category error. Deliverable: model card with held-out metrics.

## Sprint 2: recommender, service, extension

- S4 Recommender v1: similar items from RTR and ModCloth item aggregates, with a "likely to keep" ranking defined as the historical share of fit reviews. Price and color are not in those files. Price filtering uses an illustrative category band and is labeled. Deliverable: offline ranking metrics.
- S5 FastAPI service: `/predict-size`, `/recommend`, `/events`. Schema validation, tests, Docker. Deliverable: local API and OpenAPI docs.
- S6 Chrome extension, Manifest V3. Reads the size chart, price, and colors from the current page only. Panel shows the predicted size, confidence, and similar picks. Tested on a bundled demo store and saved fixture pages. Deliverable: loadable unpacked extension.
- S7 Event logging and a simulated A/B test. Synthetic shoppers, recs versus no-recs, a power calculation, returns drawn from the simulation's latent size. Deliverable: an A/B readout marked simulated.

## Sprint 3: analytics, H&M, eval

- S8 Analytics dashboard in Power BI. Locked 2026-11-11: Neel builds the .pbix on a Windows laptop. Streamlit and Dash are out of scope. The repo ships CSV extracts, a star-schema document, DAX measures, and a build guide. Publish-to-web needs a free Microsoft account and is flagged as blocked. Visuals: CTR on recs, predicted versus actual fit feedback, the A/B result, and illustrative dollars from fewer simulated fit returns.
- S9 H&M integration: purchase-history recommendations behind an adapter, compared with the S4 ranker on a synthetic fixture. The Kaggle download is implemented and refused unless the env vars are set. Deliverable: before/after ranking metrics on the fixture, with the real file marked blocked.
- S10 Eval report, README, demo notes, resume bullets filled from the generated metrics, learning site. Deliverable: published repo and site, except the H&M customer file and the Power BI publish step.

## Design calls made while building

Recorded in `docs/DESIGN_DECISIONS.md`. The short version: the prediction target is the three-way fit label, the baseline for that target is the most common class, and a second baseline recommends the most common size among reviews that said the item fit. The learned model is chosen by validation log loss, not by accuracy. User and item history features are computed from training rows only.
