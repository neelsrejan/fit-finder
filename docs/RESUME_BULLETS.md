# Resume bullets

Plain wording for a product, program, or analytics resume. These describe a public portfolio prototype. They do not describe a launched product or real shoppers.

- Built a size-and-fit prototype on the public UCSD Rent the Runway and ModCloth fit reviews (275,334 reviews in the train, validation, and test splits). Compared a most-common-class baseline, logistic regression, and LightGBM, and calibrated the learned models on a validation split. On the held-out test split the chosen model (logistic) had log loss 0.693 and accuracy 0.729, against a baseline log loss of 0.790 and accuracy of 0.718. A neighbor-size search on that model did not beat recommending the most common fit size in the category. That loss is in the model card.
- Shipped the model behind a local FastAPI service (`/predict-size`, `/recommend`, `/events`) and a Manifest V3 Chrome extension that reads a bundled demo store page. The extension is not pointed at retailer sites.
- Designed a simulated shopper experiment (recommendations versus none) with a written data-generating process, a two-proportion sample-size calculation, and a Power BI star schema. The simulated return rates were 0.329 without recommendations and 0.271 with recommendations. Dollar figures use an assumed cost per return, not a figure from the datasets.
- Wrote the Power BI data model, DAX measures, and a build guide. The .pbix file is built on a Windows laptop. Publish-to-web is waiting on a free Microsoft account. The H&M purchase-history comparison is implemented against synthetic fixtures and is waiting on a Kaggle API key.

Do not shorten these into a claim that the prototype served customers, cut returns in production, or used advanced SQL. The SQL in this project is the star-schema grain, not a warehouse job.
