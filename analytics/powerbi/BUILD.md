# Build the Power BI report

The .pbix is built on Neel's Windows laptop. This repo does not contain one, and it cannot publish the report. Publish-to-web needs a free Microsoft account signed into the Power BI service. That step is blocked until Neel does it.

Streamlit and Dash are not substitutes. The dashboard tool for this project is Power BI.

## 1. Open the extracts

1. Install Power BI Desktop if it is not already installed.
2. Get Data → Text/CSV, and load every file in `analytics/extracts/`:
   - `fact_shopper.csv`
   - `fact_event.csv`
   - `fact_model_score.csv`
   - `dim_date.csv`
   - `dim_category.csv`
   - `dim_arm.csv`
   - `assumptions.csv`
3. Set `event_date` on the fact tables and on `dim_date` to the Date type.
4. Set `returned` and `clicked` and `simulated` to True/False.

`summary.json` is for people reading the repo. Power BI does not need it.

## 2. Model view

Create the relationships in `DATA_MODEL.md`. Check that the filter direction is single, from the dimension to the fact.

Confirm `fact_model_score` is not joined to `fact_shopper`.

## 3. Measures

Open `measures.dax` and create each measure. A home for them is a measure table, or `fact_shopper` for the shopper measures and `fact_model_score` for the fit measures. `Recommendation CTR` has to see `fact_event`. If you put it on `fact_shopper`, move it.

## 4. Pages

Four pages. Put the word Simulated in the title of every page that uses `fact_shopper` or `fact_event`.

1. **Held-out fit.** Clustered column of `fit_actual` with a legend of `fit_pred`, plus the Fit Accuracy and Mean Confidence cards. A bar of accuracy by category is a stacked bar of hit versus miss, or Fit Accuracy with category on the axis. This page uses `fact_model_score` only.
2. **Simulated returns.** Return Rate with `dim_arm` on the axis. A card for Simulated Lift PP. Slicer for category.
3. **Simulated clicks.** Recommendation CTR as a card. A bar of click count by category. This page uses `fact_event`.
4. **Illustrative cost.** Illustrative Return Cost as a card, with a subtitle that reads the assumed cost from `assumptions`. Do not title this page "revenue saved" without the word illustrative.

## 5. Publish

1. Sign in to Power BI with the free Microsoft account.
2. Publish the file to My workspace.
3. Publish to web is a separate action in the service, and it makes the report public. Do that only if the public link is what you want on the resume. The report contains no reviewer names and no measurements. It does contain simulated behavior, so the page titles have to keep the simulated label after publish.

Until that account exists, the deliverable is this folder plus the CSV extracts.
