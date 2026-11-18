# Roadmap

Three sprints, ten sessions. The repo contains all ten. The public host still waits on accounts. See `docs/HOSTING.md`.

| Sprint | Sessions | Outcome |
|---|---|---|
| 1 | S1–S3 | PRD, CI, cleaned review table, calibrated size model |
| 2 | S4–S7 | Ranker, API, demo-store extension, simulated experiment |
| 3 | S8–S10 | Power BI extracts and guide, H&M adapter on fixtures, eval report and learning site |

## Now

Sessions S1 through S10 are in this repository, including tests.

## Blocked

- Render and Neon. The API blueprint and the loader are in the repo. They stay dark until Neel creates the free accounts and sets `FIT_FINDER_DATABASE_URL`. A free license cannot publish the Power BI report to the web. Extracts, DAX, and the build guide are the public dashboard artifact.
- S9 H&M customer file. The public API does not serve it: the competition license is non-commercial and academic research, with no redistribution. A private download still needs Neel's Kaggle username, key, and acceptance of the rules. The synthetic fixture comparison is the CI fallback.

## Later, if those unblock

- Retrain nothing about the UCSD model unless the H&M file is used only for the purchase ranker. The fit model and the purchase ranker answer different questions and should stay separate.
- Point the Power BI report at the same extracts. Do not paste simulated rates into a slide without the simulated label.
