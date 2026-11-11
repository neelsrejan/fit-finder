# PRD: fit-finder

## Problem

A shopper orders a size and finds out it was small or large after the garment arrives. On Rent the Runway and ModCloth, reviewers left that judgment as fit feedback. A size tool should say, before the order, how likely the size under consideration is to be the one they would call a fit, and how sure that statement is.

## User

The person this prototype is built for is a hiring manager reading a portfolio, and the shopper in the demo is fictional. There is no live traffic.

## Promise

Given a category, a numeric size, and optional measurements, the service returns:

- A fit class: small, fit, or large.
- A calibrated probability for each class. The confidence is the probability of the chosen class.
- A nearby size with a higher probability of fit, when one exists.
- A short list of other items in the category with a high historical fit rate and a usual fit size close to the shopper's size.

The confidence is only as good as the calibration on the held-out split. The model card reports the expected calibration error.

## Out of scope

- Running on Amazon, H&M, Nordstrom, Rent the Runway, ModCloth, or any other retailer site. The extension's manifest does not list those hosts.
- Claiming a return rate, a revenue number, or a click-through rate from real shoppers. Those figures in this repo are simulated or illustrative.
- Downloading the H&M Kaggle competition file without Neel's key and an explicit allow flag.
- A Streamlit or Dash dashboard. The dashboard tool is Power BI.
- Using review text, reviewer names, length feedback, or quality scores as model inputs. They are outcomes or identifiers, not things the service would know when suggesting a size.

## Success for the portfolio

- CI runs pytest on Python 3.11 and 3.12 without the UCSD download.
- Held-out metrics are produced by the training script and copied into the model card by code.
- A reader can tell, in one screen, which numbers are held-out and which are simulated.
- The learning site explains why the boundaries are drawn this way.

## Non-goals for accuracy

Beating the majority class on accuracy is a weak bar, because most reviews say "fit". The selection rule is validation log loss. Macro F1 is reported so the small and large classes are visible.
