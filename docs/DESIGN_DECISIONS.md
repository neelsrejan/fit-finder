# Design decisions

These are the calls the plan left open.

## The target is the fit label, not a size id

The reviews say small, fit, or large. That is the supervised target. A recommended size is a search around the ordered size: score P(fit) at a few neighboring sizes and pick the best. That keeps one model, instead of a separate size-id classifier that the labels do not support directly.

## Two different "most common" baselines

Accuracy against "always say fit" is the right dumb baseline for the class label, because fit is the majority review. The plan's phrase "most-common size" is the other baseline, used only for the size suggestion: recommend the modal size among training reviews in that category that said the item fit. The two baselines answer different questions and are both reported.

## Choose the model by validation log loss

Accuracy hides the small and large classes. The service shows a confidence, so a proper scoring rule is the selection rule. Macro F1 and expected calibration error are reported next to it. The winner is whichever of majority, logistic regression, and LightGBM has the lowest validation log loss after the learned models are Platt-scaled on the validation split.

## History features cannot see the row they are scoring

Item fit rates and the shopper's past mix are useful and available for a returning shopper. On the training table they are leave-one-out, so the row's own label is not in its features. Validation and test use the training aggregates only. Length, quality, rating, and review text are excluded. They are written with the review, which is after the fit is known. ModCloth's quality score is stored as `rating` for the table and is not a feature.

## Split by the shopper's review order

When a shopper has at least three reviews, the last is test and the one before is validation. Rent the Runway has a review date. ModCloth's public file does not, so within ModCloth the order is file order. That limitation is part of the data card. Shoppers with fewer reviews are bucketed by a hash of the user id so every row still lands in one split.

## Price and color are not in the UCSD files

The ranker does not invent item prices. If the caller passes a price, the service compares it to an illustrative category band and says so in `price_filter`. Color filtering runs only when the catalog row has a color. UCSD aggregates do not. The demo store has colors because the extension's job is to read the page, and the page is a fixture.

## "Likely to keep" means the reviewer said fit

There is no keep or return flag. The catalog's `fit_rate` is the share of reviews with fit equal to fit. The copy in the API says historical fit rate, not keep rate.

## The extension's trust boundary is the manifest

A content script that can read any shopping site is a different product, and it is out of scope. Host permissions are localhost and 127.0.0.1. A test fails if a retailer name shows up in the manifest. The Python parser and the content script share one page contract so CI can check the demo HTML without Chrome.

## The simulated experiment does not use the trained model as an oracle

If the simulation let the policy see the latent size, the lift would be a story about the simulator, not about uncertainty. The policy is right about direction only with a named probability. The trained model's held-out directional accuracy is reported separately and is not copied into that knob.

## H&M stays behind an adapter

`PurchaseHistorySource` has two implementations. Synthetic is the default and the one the metrics use. Kaggle is a class that can map `articles.csv` and `transactions_train.csv` once they exist on disk, plus a download function that raises unless the allow flag and both env vars are set. The build does not call it.

## Power BI gets files, not a second dashboard

Extracts are CSV so Power BI Desktop can load them without a gateway. The model-score fact is a sample of held-out predictions and has no shopper id and no measurements. The shopper and event facts are simulated and carry a column that says so. DAX divides clicks by recommendation impressions, and divides returns by shoppers. The dollar measure multiplies by the assumed cost in `assumptions.csv`.

## Learning site code on screen is main

invalid-agent Academy walks git tags because that repo was built session by session. This repo is delivered as one tree. Walkthroughs point at `main`. The video method is the same: a narration YAML, edge-tts with `en-US-AndrewNeural`, highlighted frames, and an MP4. Each clip starts with an architecture frame before the line ranges.
