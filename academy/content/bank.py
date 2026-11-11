"""Architecture quizzes. Eight questions a session. No syntax questions.

Options are one sentence and close in length so a length guess is useless.
The correct letter is the authoring key. build_site.py shuffles it.
"""

def _q(prompt, correct, a, b, c, d, why):
    return {
        "prompt": prompt,
        "correct": correct,
        "choices": {"a": a, "b": b, "c": c, "d": d},
        "why": why,
    }


QUIZZES = {
    1: [
        _q(
            "Why does the settings object refuse to print the Kaggle key?",
            "b",
            "The key is stored in the model file so the API can reload it after a restart of the process.",
            "A log of the settings object would otherwise copy the token into CI output and into local tracebacks.",
            "The key is hashed into the fit label so the calibration split can detect a rotated secret.",
            "The key selects the size scale so Rent the Runway and ModCloth share one numeric size.",
            "Secrets stay in the environment. The repr is the boundary that keeps them out of logs.",
        ),
        _q(
            "Why is the first session a skeleton with tests instead of a model?",
            "d",
            "A model trained before the schema exists can still be calibrated on the validation reviews later.",
            "The skeleton downloads both gzip files inside CI so the first green run proves the network path.",
            "The skeleton publishes the Power BI report so the later sessions have a live dashboard to extend.",
            "A green install and a green test prove the repo is runnable before any metric can be misread.",
            "CI is the contract that the portfolio runs. Metrics come after the contract holds.",
        ),
        _q(
            "Why are retailer hosts absent from the product promise?",
            "a",
            "Reading a live store page would turn a demo extension into a collector of someone else's shoppers.",
            "Retailer pages publish a shared size scale that the two UCSD files already use for training.",
            "Retailer hosts are required for the held-out split because the lab files contain no categories.",
            "Retailer hosts supply the return flag that the fit label is defined to predict directly.",
            "The trust boundary is part of the PRD. The extension is for the bundled demo store.",
        ),
        _q(
            "Why does CI install the package instead of assuming a global Python?",
            "c",
            "A global Python keeps the Kaggle key in the workflow file so forks can train without setup.",
            "A global Python skips the fixture so the job always downloads the full review gzip files.",
            "An editable install makes the tests import the same package a teammate gets from the repo.",
            "An editable install bakes the simulated lift into the package metadata as a version number.",
            "The workflow should fail on a broken import, not on a machine-specific path.",
        ),
        _q(
            "What breaks if the backlog claims a feature the PRD lists as out of scope?",
            "b",
            "The test suite starts scoring return labels that the cleaned table has stored since session two.",
            "A reader cannot tell which promise the repo is keeping and which story should not be built.",
            "The calibration split moves from validation into the test set and log loss becomes accuracy.",
            "The Chrome manifest gains the retailer hosts and the parser test starts loading live pages.",
            "The PRD is the scope boundary. The backlog is a list of stories inside that scope.",
        ),
        _q(
            "Why is the Kaggle allow flag default off in the skeleton?",
            "a",
            "The download path is documented but a fresh clone must not call Kaggle or require a token.",
            "The flag switches the fit model from logistic regression to the majority class baseline.",
            "The flag writes simulated shoppers into the held-out score file used by the model card.",
            "The flag merges ModCloth timestamps into Rent the Runway so the split becomes a pure date cut.",
            "Blocked work stays behind an explicit opt-in. Silence means do not download.",
        ),
        _q(
            "Why keep secrets in environment variables documented by an example file?",
            "c",
            "The example file is loaded by CI so the workflow can authenticate to Kaggle on every pull request.",
            "The example file stores the real token in git history and the environment only stores a pointer.",
            "A reader can see which names exist without the repository ever containing a real value.",
            "A reader can see the calibrated probabilities because the example file duplicates the model card.",
            "The example is a map of knobs. The values stay on the machine that owns the account.",
        ),
        _q(
            "What fails if session one has no test around the settings repr?",
            "d",
            "The ranker starts using illustrative prices as if they were observed item prices.",
            "The size search replaces the mode baseline inside the model card without a new training run.",
            "The demo store page begins matching retailer domains through the content script.",
            "A later edit can print the token and nothing in CI will catch the leak.",
            "The repr test is a small lock on the secret boundary. It is cheap and it stays.",
        ),
    ],
    2: [
        _q(
            "Why do two sources become one review table before any model code runs?",
            "c",
            "The join creates a return flag by pairing a ModCloth row with a Rent the Runway row.",
            "The join copies review text forward so the model can embed the written comment.",
            "One schema lets every later step share columns and lets each source keep its own gaps.",
            "One schema forces both catalogs onto a single physical size chart with shared inches.",
            "The clean table is the contract. Models should not know the raw JSON shapes.",
        ),
        _q(
            "Why is review text dropped instead of stored for a later feature?",
            "a",
            "The text is written with the label so using it would score a review the shopper has not written yet.",
            "The text is the only field that contains the illustrative price band for the category.",
            "The text is required to build the star schema date table for the simulated shoppers.",
            "The text is the collaborative filter's user vector once the Kaggle file is present.",
            "At decision time the service does not have the review. The column stays out.",
        ),
        _q(
            "Why is ModCloth quality kept out of the feature list even if it sits in rating?",
            "b",
            "Quality is the bra band and the model needs it to impute height for Rent the Runway rows.",
            "Quality is a judgment from the same review as the fit label so it leaks the outcome.",
            "Quality is the shopper id hash that the split uses to bucket one-review users.",
            "Quality is the Power BI assumed cost and the extract reads it from the review row.",
            "A stored column is not automatically an input. The feature list is the boundary.",
        ),
        _q(
            "Why does a missing ModCloth timestamp matter for the split?",
            "d",
            "It removes ModCloth from training and leaves Rent the Runway as the only calibrated source.",
            "It turns the fit label into a date so log loss can be computed on the timestamp itself.",
            "It lets the extension read ModCloth pages because the file has no time to filter on.",
            "File order is not a confirmed last review so the data card has to say the holdout is weaker there.",
            "The split still runs. The honesty constraint is to name the missing clock.",
        ),
        _q(
            "Why are the raw gzip files gitignored?",
            "a",
            "The lab page asks for a citation and does not invite the repo to republish the reviews.",
            "Gitignore is what calibrates the logistic model so the validation split stays frozen.",
            "Gitignore removes categories so the ranker can only see the demo store fixture.",
            "Gitignore is the switch that marks simulated shoppers as held-out fit reviews.",
            "CI uses a synthetic fixture. The real files stay local to a machine that downloaded them.",
        ),
        _q(
            "Why prefix user ids with the source name?",
            "c",
            "The prefix is the calibrated confidence and the API returns it as the fit class.",
            "The prefix stores the illustrative dollar cost on each review for the Power BI extract.",
            "The same numeric id can exist in both files and must not become one shopper by accident.",
            "The prefix lets the content script treat a lab user id as a retailer account id.",
            "Identity is scoped to a source. Colliding ids would invent a history that never happened.",
        ),
        _q(
            "Why impute missing height instead of dropping the row?",
            "b",
            "Dropping rows would delete the simulated A/B arms that are stored on the review table.",
            "Most rows are usable reviews and a missing measurement should not throw away the fit label.",
            "Imputation copies the test label into the training median so the split stays balanced.",
            "Imputation creates the color column the UCSD files use for the content ranker.",
            "The median is fit on training rows only. The row remains a labeled example.",
        ),
        _q(
            "What breaks if someone unions the two size columns and calls them one tape measure?",
            "d",
            "The manifest test starts failing because the size chart on the demo page changes units.",
            "The Kaggle adapter begins downloading because a shared size counts as an allow flag.",
            "The event log marks every local click as simulated because the size scale changed.",
            "A one-step nudge in the number is no longer a one-step nudge in a garment for both catalogs.",
            "Source stays a feature so the model can tell the scales apart. The card still warns about the search.",
        ),
    ],
    3: [
        _q(
            "Why is the model chosen by validation log loss rather than accuracy?",
            "a",
            "Most reviews say fit so accuracy can look strong while the probabilities stay poorly scored.",
            "Accuracy is the sample size formula and log loss is the simulated click rate.",
            "Log loss counts retailer pages and accuracy counts the demo store fixture only.",
            "Log loss requires the Kaggle file and accuracy is available from the fixture alone.",
            "The product shows a confidence. A proper score is the selection rule.",
        ),
        _q(
            "Why are there two different most-common baselines?",
            "c",
            "One baseline is the Power BI cost and the other is the extension's selected size.",
            "One baseline downloads ModCloth and the other downloads Rent the Runway during CI.",
            "One baseline is the majority fit class and the other is the usual size among fit reviews.",
            "One baseline is item-item cosine and the other is the Kaggle competition download.",
            "The class question and the size question do not share a dumb answer.",
        ),
        _q(
            "Why is history leave-one-out on the training table?",
            "b",
            "Leave-one-out copies the test set into training so the card can report a perfect log loss.",
            "The row's own label must not appear inside the features that are used to score that row.",
            "Leave-one-out replaces the category with the illustrative price so the ranker can filter.",
            "Leave-one-out is how the extension reads the size chart without a content script.",
            "Validation and test use training aggregates only. Those rows were never in the aggregate's source label.",
        ),
        _q(
            "Why calibrate on validation instead of on the test split?",
            "d",
            "The test split is where the simulated shoppers are drawn so calibration would label them real.",
            "The test split has the review text and calibration needs the text embeddings to fit.",
            "The test split is the Chrome manifest and calibration edits the host permissions.",
            "Fitting the calibrator on the test split would turn the card into a training score.",
            "Validation chooses and calibrates. Test is touched after the choice is frozen.",
        ),
        _q(
            "What does a worse directional score than the size mode mean?",
            "a",
            "The neighbor search is a weak size policy here and the card should say the mode won that comparison.",
            "The fit label model is discarded and the API must stop returning probabilities.",
            "The simulated experiment has failed its power target and the extract must be deleted.",
            "The UCSD files were the wrong download and the metrics are actually the H&M fixture.",
            "A loss on one question does not erase a win on the class probabilities. Both stay visible.",
        ),
        _q(
            "Why report macro F1 next to accuracy?",
            "c",
            "Macro F1 is the illustrative dollar total divided by the assumed cost per return.",
            "Macro F1 is the hit rate of the content ranker at ten on the held-out fit reviews.",
            "Small and large are uncommon and accuracy can hide a model that almost never names them.",
            "Small and large are the simulated arms and accuracy is only computed on the recs arm.",
            "The portfolio should show whether the rare fit mistakes are visible at all.",
        ),
        _q(
            "Why keep expected calibration error on the model card?",
            "b",
            "It is the p-value of the simulated experiment and replaces the sample size.",
            "The service shows a confidence so a reader needs to see whether confidence tracks being right.",
            "It is the share of gzip bytes that were committed despite the gitignore rule.",
            "It is the number of retailer hosts the manifest is allowed to add after session six.",
            "ECE is about the probability the UI will quote. It is not a second accuracy.",
        ),
        _q(
            "What breaks if test rows are used to compute item fit rates?",
            "d",
            "The demo page loses its price attribute and the extension shows an empty color list.",
            "The DAX return rate starts reading held-out reviews as simulated shoppers.",
            "The Kaggle flag flips on because test rates count as an accepted competition rule.",
            "The test label leaks into the feature and the reported score is no longer a forecast.",
            "History features are a promise about information available before the row is known.",
        ),
    ],
    4: [
        _q(
            "Why is the catalog an aggregate instead of a copy of the reviews?",
            "b",
            "The aggregate stores review text in a shorter column so the API can return comments.",
            "The ranker needs item-level fit rate and usual size and it should not carry shopper rows.",
            "The aggregate is the simulated shopper table and the reviews are only a date dimension.",
            "The aggregate is the Chrome panel and the reviews are the manifest host list.",
            "Ranking is an item question. The review table already did its job at training time.",
        ),
        _q(
            "Why can the ranker not treat the illustrative band as an item price?",
            "a",
            "The band is a round demo number and writing it onto items would invent prices the files do not have.",
            "The band is the calibrated probability of fit and the ranker would divide by zero.",
            "The band is the Kaggle customer id and the ranker would join the wrong source.",
            "The band is the ModCloth timestamp and the ranker would sort items by file order.",
            "A filter may mention the band. A feature may not pretend the band was observed.",
        ),
        _q(
            "Why does color filtering no-op on the UCSD catalog?",
            "d",
            "Color is stored in the fit label and filtering it would remove the majority class.",
            "Color is the validation split and filtering it would recalibrate the logistic model.",
            "Color is the event log and filtering it would mark local clicks as simulated.",
            "The public files have no color column so a color on the request cannot match an item attribute.",
            "The demo page has colors because the extension reads the page. The lab files do not.",
        ),
        _q(
            "Why is hit rate measured inside a same-category candidate set?",
            "c",
            "The candidate set is the Power BI date table and hit rate is a year-to-date total.",
            "The candidate set is the list of retailer hosts and hit rate counts blocked domains.",
            "A shopper looking at a dress is not helped by a score that mostly retrieves other categories.",
            "A shopper looking at a dress is the simulated arm and other categories are the control arm.",
            "The metric matches the product rule that the list stays in the category.",
        ),
        _q(
            "What does fit rate mean in this ranker?",
            "a",
            "It is the share of reviews whose label was fit and it is not an observed keep or return.",
            "It is the assumed cost per return multiplied by the simulated lift in percentage points.",
            "It is the sample size per arm for a two point drop at eighty percent power.",
            "It is the expected calibration error of the majority class on the test split.",
            "The word keep would overclaim. The column is a label share.",
        ),
        _q(
            "Why include review support in the score at all?",
            "b",
            "Support is the Kaggle key length and it breaks ties when the token is missing.",
            "A tiny sample can show a perfect fit rate by chance and support stops that row from dominating.",
            "Support is the number of Chrome permissions and it caps the content script matches.",
            "Support is the count of simulated clicks and it replaces the recommendation impression.",
            "The weight is small on purpose. Fit rate and size closeness still lead.",
        ),
        _q(
            "Why is this ranker not a collaborative filter?",
            "d",
            "Collaborative filtering is the settings repr and this ranker is the CI install step.",
            "Collaborative filtering needs review text and this ranker embeds the comment body.",
            "Collaborative filtering is calibration and this ranker Platt-scales the fit rate.",
            "This session only has item aggregates and purchase history is a later adapter.",
            "Mixing the two methods in one module would blur two different questions.",
        ),
        _q(
            "What breaks if the offline eval uses reviews labeled small as the positives?",
            "c",
            "The manifest would gain a retailer host because the positive class changed.",
            "The data card would lose the citation because the positive class changed.",
            "The metric would stop answering whether a known fit item is easy to retrieve.",
            "The metric would become the simulated return rate because small means a return.",
            "The positive is defined as a fit review. Changing it silently changes the question.",
        ),
    ],
    5: [
        _q(
            "Why is the API a thin edge over the saved bundle?",
            "a",
            "Retraining on each request would mix the caller's row into the model the card already reported.",
            "The edge embeds review text so the response can quote the original comment.",
            "The edge downloads Kaggle when the request body contains a category name.",
            "The edge writes the simulated experiment into the model file on every health check.",
            "The bundle is the frozen choice. The route scores and returns.",
        ),
        _q(
            "Why return 503 when the model file is missing?",
            "c",
            "A missing file should be treated as a perfect confidence so the demo panel still renders a size.",
            "A missing file should fall back to scraping a retailer size chart from the request URL.",
            "A missing file is a failed dependency and a quiet guess would look like a real prediction.",
            "A missing file means the simulated lift should be returned as the fit probability.",
            "The client can show the offline message. That is an honest failure.",
        ),
        _q(
            "Why is simulated false on rows posted to the events route?",
            "b",
            "Those rows are the A/B readout and the flag hides the fact that they are generated shoppers.",
            "Those rows are requests this process actually received and they are still not store traffic.",
            "Those rows are held-out reviews and the flag marks them as the model card sample.",
            "Those rows are Kaggle transactions and the flag marks them as the competition file.",
            "The disclaimer splits local demo calls from the simulated extract. The flag is that split.",
        ),
        _q(
            "Why validate the body with a schema instead of a free JSON object?",
            "d",
            "The schema stores the Kaggle key in the OpenAPI document so clients can copy it.",
            "The schema calibrates the probabilities before the model sees the size.",
            "The schema chooses the train split by rejecting categories that are too rare.",
            "A typed body fails fast on a missing size and documents the contract.",
            "The three routes are the product surface. Their fields should be boring and explicit.",
        ),
        _q(
            "Why does the Docker image copy the model and not the raw gzip files?",
            "a",
            "The running service needs the bundle and the catalog and it does not need to republish the reviews.",
            "The image trains LightGBM during docker build so the committed metrics can change per machine.",
            "The image includes the Chrome extension and serves retailer pages from the container.",
            "The image includes the Power BI file and publishes it when the container starts.",
            "Ship the artifact the route loads. Leave the research dump on the machine that downloaded it.",
        ),
        _q(
            "What breaks if the recommend route silently invents prices for UCSD items?",
            "c",
            "The settings repr starts printing the Kaggle key because the price field is a secret.",
            "The split starts using price as a timestamp because ModCloth has no review date.",
            "Clients would treat a made-up price as data and the illustrative-band note would be a lie.",
            "Clients would receive the simulated sample size as a price and the power formula would change.",
            "The response already names the price filter. The items still have no observed price.",
        ),
        _q(
            "Why keep OpenAPI docs as a deliverable?",
            "b",
            "The docs page runs the simulated experiment and writes the Power BI extracts.",
            "A hiring manager can see the three routes and the fields without reading the framework.",
            "The docs page is the learning-site quiz and the pass mark is stored in the schema.",
            "The docs page downloads the UCSD files when a browser opens the local port.",
            "The surface area of the product should be inspectable in one page.",
        ),
        _q(
            "Why should the events route not be the writer for the A/B extract?",
            "d",
            "The route is faster and the extract should be as large as the full review table.",
            "The route calibrates the model and the extract should store the new coefficients.",
            "The route is the content script and the extract should store page HTML.",
            "The experiment is a batch with a seed and mixing it into live demo posts would blur the label.",
            "Two writers would make simulated and not-simulated share a file by accident.",
        ),
    ],
    6: [
        _q(
            "Why is the manifest the trust boundary for the extension?",
            "a",
            "Host permissions decide which pages the content script can read and retailer pages are not on the list.",
            "Host permissions calibrate the fit model when the panel asks for a size.",
            "Host permissions store the simulated return rate that the panel prints as confidence.",
            "Host permissions select the Kaggle competition and start the download on install.",
            "A wider match is a different product. The test locks the list that shipped.",
        ),
        _q(
            "Why does CI parse the demo HTML in Python?",
            "c",
            "The Python parser publishes the Power BI report from the size chart cells.",
            "The Python parser trains the logistic model on the fixture colors and price.",
            "Chrome is not required in CI and the page contract can still be checked on every run.",
            "Chrome is required in CI and the Python parser is only a fallback for the Kaggle file.",
            "The content script and the parser share attributes. The test guards that share.",
        ),
        _q(
            "Why is the demo store a fixture instead of a saved retailer page?",
            "b",
            "A saved retailer page is smaller and it includes the return flag the model needs.",
            "A saved retailer page would copy someone else's store into the repo.",
            "A fixture cannot include a size chart so the panel has nothing to read.",
            "A fixture is the held-out test split rendered as HTML for the model card.",
            "The page exists to exercise the contract. It does not pretend to be a merchant.",
        ),
        _q(
            "What breaks if the content script matches every https page?",
            "d",
            "The fit label gains a fourth class because the script sees more colors.",
            "The validation split moves into the browser because the script sends timestamps.",
            "The illustrative price band becomes an observed price because the script averages pages.",
            "The extension starts reading shopper pages it was explicitly not allowed to touch.",
            "The PRD's out-of-scope list would be false the moment the match changed.",
        ),
        _q(
            "Why show an offline message when the API is down?",
            "a",
            "A blank panel or a made-up size would look like a prediction the service did not make.",
            "An offline message retrains the bundle in the browser and writes a new model card.",
            "An offline message switches the ranker to the Kaggle file stored in the extension.",
            "An offline message marks the page as a simulated shopper and logs a return.",
            "Failure is part of the demo. The copy should say the local API is not running.",
        ),
        _q(
            "Why does the panel send the page price and then warn that the band is illustrative?",
            "c",
            "The warning hides a real item price that the UCSD catalog stores and the API returns.",
            "The warning is the calibration error and the price is the log loss of the chosen model.",
            "The page has a price because it is a fixture and the catalog still has no item price to filter on.",
            "The page has a price because it is a held-out review and the catalog stores that review's text.",
            "The extension may pass what it read. The service may not pretend the lab data confirmed it.",
        ),
        _q(
            "Why keep the storyboard labeled as a drawing?",
            "b",
            "A drawing is the model card and calling it a drawing updates the held-out accuracy.",
            "Calling a drawing a user study would invent shoppers the project does not have.",
            "Calling a drawing a capture is required so the Power BI publish step can embed it.",
            "Calling a drawing a fixture lets CI skip the parser test on the demo page.",
            "The demo doc is part of the honesty rule. The GIF is not traffic and not a retailer.",
        ),
        _q(
            "What does the parser test fail to prove?",
            "d",
            "It fails to prove that review text was dropped because it loads the gzip files.",
            "It fails to prove that log loss beat the baseline because it scores the model.",
            "It fails to prove that the Kaggle flag is off because it calls the download.",
            "It proves the fixture matches the contract and it does not prove Chrome rendered the panel.",
            "That limit is why the README says how to load the unpacked extension by hand.",
        ),
    ],
    7: [
        _q(
            "Why is the shopper experiment not allowed to read the trained model?",
            "b",
            "The model file is too small and the experiment needs the raw gzip files to draw shoppers.",
            "Using the model as an oracle would make the lift a story about the simulator's hidden size.",
            "The model is the manifest and the experiment would add retailer hosts if it loaded the bundle.",
            "The model is the DAX measure and the experiment would overwrite the star schema.",
            "The directional accuracy stays on the model card. The sim has its own named probability.",
        ),
        _q(
            "Why write the probabilities as named constants?",
            "a",
            "A reader can see the data-generating process and rebuild the extract by changing a knob on purpose.",
            "A reader can paste the constants into the model card as held-out log loss without retraining.",
            "The constants are the UCSD fit counts and editing them updates the data card row total.",
            "The constants are the Kaggle credentials and editing them enables the download.",
            "Hidden knobs become fake findings. Named knobs stay assumptions.",
        ),
        _q(
            "Why is the dollar figure called illustrative?",
            "d",
            "The figure is the test accuracy multiplied by the number of categories in the catalog.",
            "The figure is a sum of observed return costs in the Rent the Runway file.",
            "The figure is the content ranker's hit rate converted to currency by the lab license.",
            "Neither dataset has a cost per return so the total is an assumption times a simulated count.",
            "The extract carries the assumption in its own parameter table for the same reason.",
        ),
        _q(
            "What does the sample-size function answer?",
            "c",
            "It answers how many UCSD reviews are required before LightGBM can replace logistic regression.",
            "It answers how many retailer pages the extension may read before the manifest test fails.",
            "It answers how large an equal-allocation test must be to detect a planned two point drop.",
            "It answers how large the Kaggle file is so the adapter can refuse the download.",
            "The planning lift is not the lift this seed happened to draw. The function says so by its inputs.",
        ),
        _q(
            "Why mark every simulated row in the data and not only in a README sentence?",
            "a",
            "A chart can be copied without the README and the column still says the row is not traffic.",
            "A column named simulated calibrates the probabilities when Power BI refreshes the file.",
            "A column named simulated is the fit label and Power BI uses it as fit_actual.",
            "A column named simulated stores the bra band so the report can impute height.",
            "Labels that travel with the row survive a screenshot. A preface does not.",
        ),
        _q(
            "What breaks if the simulated lift is pasted into the model card as a return reduction?",
            "c",
            "The card's log loss becomes the click rate and the ECE row is deleted.",
            "The card's per-category table becomes the demo store size chart.",
            "A reader would treat the fit model as a live return test.",
            "A reader would think the extension started matching retailer hosts.",
            "The two numbers answer different questions and the boundary is the whole point of the disclaimer.",
        ),
        _q(
            "Why use a latent size instead of the review label as the sim's return?",
            "b",
            "The review label is a return flag and the latent size would duplicate it.",
            "The reviews have no return flag so a return in the sim has to be generated and named as such.",
            "The latent size is the Kaggle customer id and the review label is the article id.",
            "The latent size is the validation fold and the review label is the test fold.",
            "Using the fit label as a return would smuggle a new definition into an old column.",
        ),
        _q(
            "Why keep the policy-right probability distinct from directional accuracy?",
            "d",
            "They are the same quantity and the card copies one into the other after each training run.",
            "Directional accuracy is the simulated CTR and the probability is the assumed unit cost.",
            "Directional accuracy is the manifest length and the probability is the parser's selected size.",
            "One is an assumption of the generator and the other is a measured score of the size search.",
            "Coupling them would let a tuning of the story rewrite a held-out number or the reverse.",
        ),
    ],
    8: [
        _q(
            "Why are held-out scores and simulated shoppers different facts?",
            "a",
            "They are not the same people and a join would invent a relationship the data does not have.",
            "They are the same people and a join is required before any DAX measure can divide.",
            "The score fact is the Kaggle file and the shopper fact is the raw gzip archive.",
            "The score fact is the extension popup and the shopper fact is the content script.",
            "Shared category names do not make the rows the same events.",
        ),
        _q(
            "Why is Power BI required instead of a notebook chart?",
            "c",
            "A notebook chart is the only tool that can read the simulated flag column.",
            "A notebook chart calibrates the model and Power BI cannot load a CSV.",
            "The dashboard skill this portfolio is practicing is Power BI and the guide is the deliverable.",
            "The dashboard skill this portfolio is practicing is a live retailer embed of the demo store.",
            "The .pbix still waits on a Windows build. The extracts do not wait.",
        ),
        _q(
            "Why is publish-to-web blocked in the repo?",
            "b",
            "Publish-to-web needs the Kaggle key and the competition rules acceptance.",
            "Publish-to-web needs Neel's Microsoft account inside the Power BI service.",
            "Publish-to-web needs the raw review text so the report can show comments.",
            "Publish-to-web needs the extension to match retailer hosts before the link works.",
            "The guide says the step. The repo cannot sign in as him.",
        ),
        _q(
            "Why does the category dimension include categories from both facts?",
            "d",
            "So the simulated return rate is computed on held-out reviews without a second measure.",
            "So the fit accuracy measure counts simulated shoppers as labeled reviews.",
            "So the illustrative cost is divided by the test log loss inside one visual.",
            "So a category slicer has a key to filter each fact without implying the facts are one table.",
            "The relationship is many-to-one onto the dimension. There is still no fact-to-fact relationship.",
        ),
        _q(
            "Why is click-through rate defined on the event fact?",
            "a",
            "An impression and a click are different events and the shopper row would collapse them.",
            "The event fact is the model card and the click is the chosen model's accuracy.",
            "The event fact is the clean review table and the click is the fit label.",
            "The event fact is the Kaggle transaction file and the click is a purchase.",
            "CTR is a ratio of event types. The grain of the fact has to be the event.",
        ),
        _q(
            "What does the assumed-cost row in the parameter table protect?",
            "c",
            "It protects the Kaggle token by storing it next to the DAX measures.",
            "It protects the test split by storing the held-out labels in the cost column.",
            "It keeps the unit cost next to the data so a dollar visual can name its assumption.",
            "It keeps the unit cost inside the logistic coefficients so retraining updates the dollars.",
            "A number without its assumption becomes a fake saved-revenue claim.",
        ),
        _q(
            "Why omit shopper measurements from the score extract?",
            "b",
            "Measurements are required for the DAX date table and the extract builds them from height.",
            "The score sample should not carry fields that make a person easier to recognize.",
            "Measurements are the simulated arm labels and the extract would reveal the seed.",
            "Measurements are the content script's size chart and the extract would duplicate the demo page.",
            "Category and the probability vector are enough for the predicted-versus-actual page.",
        ),
        _q(
            "What breaks if one visual plots return rate and fit accuracy on the same axis without a label?",
            "d",
            "The axis becomes the size chart and the extension reads it as a bust measurement.",
            "The axis becomes the validation log loss and calibration is refit in the browser.",
            "The axis becomes the Kaggle download progress and the allow flag turns on.",
            "A reader cannot tell a simulated return from a held-out fit label and the boundary collapses.",
            "Page titles in the build guide exist so that collapse has to be a deliberate edit.",
        ),
    ],
    9: [
        _q(
            "Why is purchase history a different question from fit feedback?",
            "c",
            "Purchases are the fit label under another name and the same model should score both.",
            "Purchases include the review text the clean step kept for the collaborative filter.",
            "A purchase says an item was bought and a fit label says a size was called small fit or large.",
            "A purchase is the simulated return and a fit label is the assumed unit cost.",
            "The adapter exists so the second question can arrive later without rewriting the first model.",
        ),
        _q(
            "Why does the download function raise when the allow flag is unset?",
            "a",
            "A documented path should not open a socket just because the code is importable.",
            "An unset flag means the fit model must be replaced by item-item cosine immediately.",
            "An unset flag means CI should commit the competition CSV into the repository.",
            "An unset flag means the demo store should proxy a retailer checkout page.",
            "The flag is the human opt-in. The missing key is a second lock.",
        ),
        _q(
            "Why compare the two rankers on the synthetic fixture?",
            "b",
            "The fixture is the held-out UCSD test split and the comparison updates the model card accuracy.",
            "The real file is absent and a comparison still has to run on data the repo is allowed to ship.",
            "The fixture is the Power BI extract and the comparison is a DAX measure.",
            "The fixture is the Chrome panel and the comparison counts host permissions.",
            "The note on the metric says the preference was planted. That disclosure is part of the result.",
        ),
        _q(
            "What would still be false after the Kaggle file is downloaded?",
            "d",
            "The fit model would automatically become a purchase model with no new training decision.",
            "The simulated shoppers would become H&M customers because the file arrived.",
            "The extension would be allowed to run on the retail site because the file arrived.",
            "The fit model would still be a fit model until someone deliberately trains a different question.",
            "Unblocking a file is not a license to rename every metric in the report.",
        ),
        _q(
            "Why map Kaggle columns inside the adapter instead of in the ranker?",
            "a",
            "The ranker should see one column contract and the messy source names should stop at the edge.",
            "The ranker should see the raw competition header so the hit rate can use every extra field.",
            "The adapter should store the API token in the article table for the content script.",
            "The adapter should overwrite the UCSD catalog with customer ids from the competition.",
            "Same pattern as the UCSD clean step. Source shapes do not leak inward.",
        ),
        _q(
            "Why is a planted category preference disclosed?",
            "c",
            "The preference is an observed H&M segment and disclosure is optional decoration.",
            "The preference is the calibration method and disclosure replaces expected calibration error.",
            "Without the disclosure a reader could think the fixture hit rate was a customer result.",
            "Without the disclosure the settings repr would start printing the Kaggle key.",
            "Planted structure is allowed in a fixture. Quiet planted structure is not.",
        ),
        _q(
            "Why keep item-item cosine off the UCSD fit model?",
            "b",
            "Cosine needs the review text embeddings that the clean step stored for this purpose.",
            "The fit model is supervised on a size label and cosine here is a purchase-neighborhood score.",
            "Cosine is the sample size formula and it belongs in the model card ECE row.",
            "Cosine is the manifest matcher and it belongs in the content script.",
            "Putting them in one score would make a hiring manager think one number answered both.",
        ),
        _q(
            "What does the env example file owe a reader about this session?",
            "d",
            "It owes the real token so a fork can download the competition without an account.",
            "It owes the held-out log loss so the example file can replace the model card.",
            "It owes the simulated lift so the example file can replace the disclaimer.",
            "It owes the variable names and a warning to leave the download flag unset.",
            "Names without values are the whole pattern for secrets in this repo.",
        ),
    ],
    10: [
        _q(
            "Why generate the resume bullets from the metrics JSON?",
            "b",
            "The JSON is the simulated seed and the bullets should change when the seed changes only.",
            "A hand-typed digit can drift from the training run and the script keeps the sentence attached to the file.",
            "The JSON is the Kaggle key and the bullets publish it in a safer sentence.",
            "The JSON is the manifest and the bullets list the retailer hosts that were approved.",
            "The prose is fixed. The digits are formatted. That is the boundary.",
        ),
        _q(
            "Why refuse the phrase advanced SQL in the bullets?",
            "a",
            "The project documents a star schema and DAX and it does not contain a warehouse workload to claim.",
            "The project runs a warehouse nightly and the phrase would understate that job.",
            "The phrase is required by the Power BI service before publish-to-web is enabled.",
            "The phrase is the name of the calibration method used on the validation split.",
            "Plain wording is a product decision. Inflated skill words fail a careful reader.",
        ),
        _q(
            "Why can the learning site quizzes ignore syntax?",
            "d",
            "Syntax quizzes are stored in the model bundle and the site only renders confidence.",
            "Syntax quizzes are the CI job and the site only renders the workflow YAML.",
            "Syntax quizzes are how the extension parses retailer pages it does not match.",
            "The goal is to defend the boundaries in an interview and not to recite a line of the clean step.",
            "The videos still walk lines. The quiz asks why the line's module exists.",
        ),
        _q(
            "Why put an architecture frame before the line walkthrough?",
            "c",
            "The frame replaces the code so the video can skip the file that implements the idea.",
            "The frame shows the Kaggle token so the walkthrough can explain how to paste it.",
            "A viewer should know what the file owes its neighbors before the highlight starts moving.",
            "A viewer should memorize the line numbers because the quiz asks for them.",
            "The overview is the map. The segments are the streets.",
        ),
        _q(
            "What would make the eval report dishonest even if every digit matches the JSON?",
            "a",
            "A heading that calls the simulated lift a live return reduction while leaving the digit untouched.",
            "A heading that says the logistic model won validation log loss when the JSON says it did.",
            "A heading that says the H&M file was not downloaded when the JSON says it was blocked.",
            "A heading that says the size search lost to the mode when the JSON says it lost.",
            "The words around a true digit can still lie. The report's job is both.",
        ),
        _q(
            "Why is the learning site static files plus a Pages workflow?",
            "b",
            "A server would let the quizzes update the trained model when a reader submits a score.",
            "A static site can be studied from the repo and the workflow publishes it without a paid host.",
            "A static site scrapes retailer pages at build time and embeds the captured HTML.",
            "A static site stores the Kaggle key in the quiz hash so the download can run in the browser.",
            "Progress stays in the browser on purpose. There is no account on the site.",
        ),
        _q(
            "Why point the walkthroughs at main instead of a session tag?",
            "d",
            "Tags are required because the fit label changes meaning in every session.",
            "Tags hold the raw gzip files and main holds only the synthetic fixture.",
            "Tags are the simulated arms and main is the control arm of the experiment.",
            "This repo was delivered as one tree so the code on screen is the code a reader clones.",
            "The other academy used tags because it grew session by session. This one did not.",
        ),
        _q(
            "What should a reader do with a metric that is not in the JSON files?",
            "c",
            "Add it to the resume if it makes the accuracy sound higher than the card.",
            "Add it to the Power BI title if it makes the simulated page sound observed.",
            "Leave it out until a script writes it because every quoted number has to have a generator.",
            "Leave it in the extension popup as a confidence if the API is down.",
            "That rule is how the portfolio stays checkable.",
        ),
    ],
}


def _balance() -> None:
    """Stop a longest-or-shortest guess without adding a second sentence.

    When the correct option is strictly the longest, a wrong option grows by a
    short clause until it is longer. When the correct option is strictly the
    shortest, it grows until it is not.
    """
    grow = " for this boundary"
    for questions in QUIZZES.values():
        for question in questions:
            choices = question["choices"]

            def lengths():
                return {key: len(choices[key]) for key in "abcd"}

            def grow_key(key: str, times: int) -> None:
                text = choices[key]
                end = ""
                if text.endswith("."):
                    text, end = text[:-1], "."
                text = text + (grow * times)
                choices[key] = text + end

            correct = question["correct"]
            # Lift the correct option off the unique minimum.
            for _ in range(4):
                current = lengths()
                shortest = min(current.values())
                if current[correct] != shortest:
                    break
                if sum(value == shortest for value in current.values()) > 1:
                    break
                grow_key(correct, 1)
            # Lift one wrong option just past the correct option when the correct option leads.
            for _ in range(6):
                current = lengths()
                longest = max(current.values())
                if current[correct] != longest:
                    break
                if sum(value == longest for value in current.values()) > 1:
                    break
                wrong = [key for key in "abcd" if key != correct]
                host = max(wrong, key=lambda key: current[key])
                grow_key(host, 1)
            for _ in range(8):
                current = list(lengths().values())
                ordered = sorted(current)
                median = (ordered[1] + ordered[2]) / 2
                if median and all(0.75 * median <= value <= 1.25 * median for value in current):
                    break
                short_key = min(choices, key=lambda key: len(choices[key]))
                grow_key(short_key, 1)


_balance()


def _place_letters() -> None:
    """Put the correct text in the slot whose shuffled letter keeps each session near even."""
    import hashlib
    import random

    def salt(session: int, number: int) -> str:
        qid = f"s{session}q{number}"
        return hashlib.sha256(f"ff-quiz|{session}|{qid}|v1".encode()).hexdigest()[:16]

    def published(session: int, number: int, slot: int) -> str:
        texts = ["w0", "w1", "w2", "w3"]
        texts[slot] = "CORRECT"
        random.Random(salt(session, number)).shuffle(texts)
        return "abcd"[texts.index("CORRECT")]

    for session, questions in QUIZZES.items():
        counts = {letter: 0 for letter in "abcd"}
        for number, question in enumerate(questions, 1):
            options = [(published(session, number, slot), slot) for slot in range(4)]
            letter, slot = min(options, key=lambda item: (counts[item[0]], item[1]))
            counts[letter] += 1
            correct_text = question["choices"][question["correct"]]
            others = [question["choices"][key] for key in "abcd" if question["choices"][key] != correct_text]
            ordered = others[:]
            ordered.insert(slot, correct_text)
            question["choices"] = {key: ordered[index] for index, key in enumerate("abcd")}
            question["correct"] = "abcd"[slot]


_place_letters()





