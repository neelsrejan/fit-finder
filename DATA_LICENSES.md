# Data licenses

## Code

The code in this repository is MIT. See `LICENSE`.

## UCSD clothing fit reviews

Source page: [McAuley Lab datasets, Clothing Fit Data](https://cseweb.ucsd.edu/~jmcauley/datasets.html#clothing_fit).

Files the download script requests:

- `https://mcauleylab.ucsd.edu/public_datasets/data/modcloth/modcloth_final_data.json.gz`
- `https://mcauleylab.ucsd.edu/public_datasets/data/renttherunway/renttherunway_final_data.json.gz`

The page asks for this citation if the data is used:

Misra, Rishabh, Mengting Wan, and Julian McAuley. "Decomposing Fit Semantics for Product Size Recommendation in Metric Spaces." RecSys, 2018.

The datasets page does not ship a separate license file with the gzip archives. It presents the files as public research data and asks for the citation. This repo follows that request.

The paper's author also published the same two files on Kaggle as `rmisra/clothing-fit-dataset-for-size-recommendation` under Creative Commons Attribution 4.0. This repo downloads the lab URLs, which need no account, and cites the paper. It does not re-upload the reviews.

What this repo does with the files:

- The download script writes them under `data/raw/`, which is gitignored.
- The cleaned Parquet table is gitignored as well.
- Review text and ModCloth `user_name` are dropped during cleaning and are not stored in the Parquet columns.
- Committed artifacts that come from the files are aggregates and model outputs: the model card metrics, a sample of held-out predictions without measurements, and an item catalog of fit rates. They are not a republication of the reviews.
- `data/fixtures/reviews.csv` is synthetic. It is not a slice of the UCSD files.

The reviews were originally written by people on ModCloth and Rent the Runway. Using the research release for a public portfolio is within the "cite the paper" request on the lab page. It is not a claim of ownership, and it is not a product partnership with either retailer.

## H&M Personalized Fashion Recommendations

Competition page: `h-and-m-personalized-fashion-recommendations` on Kaggle.

The data page states `DATA ACCESS AND USE: Non-Commercial Purposes & Academic Research.` RelBench records the same rules as non-commercial and academic research only, with no redistribution. A public portfolio API is not that use. The file is not in this repo, was not downloaded, and is not loaded into the hosted database. `transactions_train.csv` is about 31.8 million rows, which also does not fit the free 1 GB database beside the UCSD table.

The synthetic fixture under the H&M adapter is original to this repo. It is the CI and offline fallback for that comparison. A private download still requires the competition rules accepted in a browser, then `KAGGLE_USERNAME`, `KAGGLE_KEY`, and `FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD=1`. That download must not be copied into the public store.

## Illustrative price bands

`ILLUSTRATIVE_PRICE_BANDS` in `src/fit_finder/recommend/catalog.py` are round numbers chosen for the demo filter. They are not prices observed in either dataset.
