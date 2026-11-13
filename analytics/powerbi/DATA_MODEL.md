# Power BI data model

The report has two grains. Do not plot them on the same visual as if they were one fact.

## Held-out model scores

`fact_model_score` is a sample of test-split predictions from the trained size model.

| Column | Meaning |
|---|---|
| source | renttherunway or modcloth |
| category | cleaned category, joins to dim_category |
| fit_actual | the reviewer's label |
| fit_pred | the model's class |
| p_small, p_fit, p_large | calibrated probabilities |
| confidence | max probability |
| model | chosen model name |

There is no user id, no measurement, and no date. It is not a time series. The relationship to `dim_category` is many-to-one on `category`.

## Simulated shoppers

`fact_shopper` is one simulated shopper from `src/fit_finder/events/ab.py`.

| Column | Meaning |
|---|---|
| shopper_id | row number in the simulation |
| category | joins to dim_category |
| arm | recs or no_recs, joins to dim_arm |
| event_date | a spread across March 2024 so the date table has rows. The date is not an observed session time |
| returned | simulated return |
| clicked | simulated click on a recommendation. Control rows are false |
| simulated | always true |
| illustrative_return_cost | returned, times the assumed unit cost |

`fact_event` is the same simulation exploded into impression, recommendation_impression, and click rows. CTR uses this fact, not the shopper fact, so an impression and a click are different events.

## Dimensions

- `dim_date` on `event_date`
- `dim_category` on `category`
- `dim_arm` on `arm`
- `assumptions` is a one-row parameter table. It does not need a relationship. The dollar measure reads `assumed_cost_per_return` from it.

## Relationships to create

- fact_shopper[event_date] to dim_date[event_date], many to one, single direction
- fact_shopper[category] to dim_category[category]
- fact_shopper[arm] to dim_arm[arm]
- fact_event[event_date] to dim_date[event_date]
- fact_event[category] to dim_category[category]
- fact_event[arm] to dim_arm[arm]
- fact_model_score[category] to dim_category[category]

Do not relate fact_model_score to fact_shopper. They are not the same shoppers. One is a held-out review score. The other is a simulated person.

## What each visual is allowed to say

- Fit class predicted versus actual: fact_model_score only. Title it as held-out fit feedback.
- Return rate by arm: fact_shopper only. Title it as simulated.
- CTR: fact_event only. Title it as simulated.
- Illustrative dollars: fact_shopper[illustrative_return_cost], and the subtitle names the assumed unit cost.
