# Model card

The size model predicts the fit feedback a reviewer left: small, fit, or large.
It does not predict a return. The datasets do not have a return flag.

Chosen model: **logistic**.
Selection rule: lowest validation log loss after calibration.

Split counts (reviews):

- Train: 197419
- Validation (calibration): 38835
- Test: 39080

Test metrics. Log loss uses the natural log and the three-class probability vector.

| Model | Log loss | Accuracy | Macro F1 | ECE |
|---|---:|---:|---:|---:|
| majority | 0.7904 | 0.7180 | 0.2786 | 0.0052 |
| logistic | 0.6925 | 0.7285 | 0.3818 | 0.0149 |
| lightgbm | 0.7017 | 0.7217 | 0.3056 | 0.0161 |

Directional size suggestion on the test rows, using the chosen model.
A correct suggestion stays put when the review said fit, moves up when the review said small, and moves down when the review said large.

- Chosen model directional accuracy: 0.1212
- Most-common-fit-size baseline directional accuracy: 0.2474

The neighbor-size search lost to that simpler rule on this test split. The class model is still the one selected for the fit label and the confidence. The search is what `/predict-size` returns as `recommended_size`, and this card is where that loss is recorded. Rent the Runway and ModCloth do not share a size scale, which is one reason a two-step nudge in `size_index` is a weak policy.

Per-category accuracy for the chosen model, largest test categories first.

| Category | n | Accuracy |
|---|---:|---:|
| dress | 13065 | 0.7404 |
| gown | 5555 | 0.7937 |
| bottoms | 3909 | 0.6938 |
| tops | 2857 | 0.6899 |
| sheath | 2766 | 0.7570 |
| new | 2048 | 0.6577 |
| outerwear | 1622 | 0.6313 |
| dresses | 1550 | 0.7342 |
| jumpsuit | 795 | 0.7333 |
| top | 772 | 0.7215 |
| shift | 708 | 0.7302 |
| maxi | 532 | 0.7914 |
| romper | 439 | 0.7494 |
| jacket | 395 | 0.7519 |
| sale | 377 | 0.6154 |

Calibration is Platt scaling on the validation split (`CalibratedClassifierCV` with a frozen estimator).
The majority baseline is not calibrated further. Its probabilities are the training class mix.

Features are measurements, the ordered size, category, and history rates computed from training rows only.
Review text, reviewer name, length, and quality are not inputs.
