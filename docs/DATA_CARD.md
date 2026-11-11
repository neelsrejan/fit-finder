# Data card

Public UCSD Rent the Runway and ModCloth fit reviews, cleaned into one table. Counts below were computed from the local Parquet file by the profile step in this session and stored in `docs/metrics/data_profile.json`.

| | |
|---|---:|
| Rows kept | 275,334 |
| Rent the Runway | 192,544 |
| ModCloth | 82,790 |
| Shoppers | 153,529 |
| Items | 7,228 |
| Categories | 75 |
| Fit | 198,815 |
| Small | 38,753 |
| Large | 37,766 |

Rows missing a fit label, a size, a user id, or an item id were dropped. On these two files that removed none of the published rows. The lab page's counts match: 192,544 and 82,790.

## Missing measurements

| Field | Share missing |
|---|---:|
| height_in | 0.017 |
| bust_band | 0.089 |
| age | 0.304 |
| weight_lbs | 0.410 |
| review_date | 0.301 |

Age, weight, and review date are missing on ModCloth, which is about 30% of the rows. Weight is also missing on some Rent the Runway rows, which is why weight's missing share is higher than 30%. The model imputes numeric gaps with the training median. It does not drop the row.

## What was removed on purpose

Review text, review summary, and ModCloth `user_name` are not columns. Length and quality are not model inputs. ModCloth's quality value is kept in `rating` so the table still has a score, and the feature list does not include `rating`.

## Size

`size_index` is the numeric size in the file. The two sources do not document a shared size scale. The model sees `source` as a feature so it can treat them differently. A one-step change in `size_index` is not a one-step change in a physical measurement across both catalogs. The model card's directional result should be read with that in mind.

## Split note

Rent the Runway orders a shopper's reviews by `review_date`. ModCloth has no timestamp, so the order inside that source is file order. The last review is not a confirmed "most recent" review for ModCloth.

## What is not in the file

No price. No color. No return flag. No keep flag. `fit_rate` in the catalog is the share of reviews whose label is fit.
