# Eval report

Two kinds of numbers live here. Held-out fit metrics come from the public UCSD reviews.
The shopper experiment and the H&M comparison do not.

## Held-out fit model

Chosen model `logistic` test log loss 0.6925, accuracy 0.7285, macro F1 0.3818, ECE 0.0149.
Majority baseline test log loss 0.7904 and accuracy 0.7180.
Directional accuracy 0.1212 versus 0.2474 for the most-common-fit-size rule.

## Content ranker

Hit rate @10 0.3488 and MRR 0.1367 on 797 held-out fit reviews.
held-out fit review ranked among same-category items.

## Simulated A/B

SIMULATED. Not store traffic.

Return rate, no recommendations: 0.3287.
Return rate, recommendations: 0.2707.
Lift: 5.80 percentage points.
Recommendation CTR: 0.1177.
Illustrative dollars, at $20 assumed per return: 4640.00.
Sample size per arm to detect a 2 point drop from the control rate, 80% power, alpha 0.05: 8518.

## H&M comparison

H&M Kaggle file was not downloaded. Metrics are the synthetic fixture.

Synthetic content hit rate @3: 0.5750.
Synthetic item-item CF hit rate @3: 0.1000.
Content ranking uses planted fit_rate and category. Collaborative filtering uses planted category preference in the purchases. Neither number is an H&M customer metric.
