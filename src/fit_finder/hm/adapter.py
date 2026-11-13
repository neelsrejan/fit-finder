"""H&M purchase-history source.

The real file is the Kaggle competition
`h-and-m-personalized-fashion-recommendations`. This repo does not download
it. `KaggleHMSource` is the documented path. `SyntheticHMSource` is what
tests and the comparison metrics use.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from fit_finder.config import load_settings


class HMDownloadBlocked(RuntimeError):
    """Raised when a download is requested and the gate is closed."""


class PurchaseHistorySource:
    """Articles and transactions in the columns the rankers share."""

    name = "base"

    def articles(self) -> pd.DataFrame:
        raise NotImplementedError

    def transactions(self) -> pd.DataFrame:
        raise NotImplementedError


class SyntheticHMSource(PurchaseHistorySource):
    """Small fixture with the same columns a Kaggle extract would be mapped to."""

    name = "synthetic_fixture"

    def __init__(self, n_users: int = 80, n_items: int = 24, seed: int = 7) -> None:
        self.n_users = n_users
        self.n_items = n_items
        self.seed = seed

    def articles(self) -> pd.DataFrame:
        import numpy as np

        rng = np.random.default_rng(self.seed)
        categories = np.array(["dress", "top", "jeans", "skirt"])
        colors = np.array(["black", "navy", "red", "white"])
        rows = []
        for index in range(self.n_items):
            rows.append(
                {
                    "item_id": f"syn-{index:03d}",
                    "category": str(categories[index % len(categories)]),
                    "color": str(colors[index % len(colors)]),
                    "list_price": float(40 + (index % 6) * 15),
                    "fit_rate": float(rng.uniform(0.55, 0.9)),
                }
            )
        return pd.DataFrame(rows)

    def transactions(self) -> pd.DataFrame:
        """Each user buys a preferred category, plus a little noise.

        The preference is what makes collaborative filtering find a signal
        on this fixture. It is planted. The readout says so.
        """
        import numpy as np

        rng = np.random.default_rng(self.seed + 1)
        articles = self.articles()
        rows = []
        for user in range(self.n_users):
            preferred = ["dress", "top", "jeans", "skirt"][user % 4]
            pool = articles[articles["category"].eq(preferred)]
            other = articles[~articles["category"].eq(preferred)]
            picks = list(rng.choice(pool["item_id"], size=4, replace=False))
            picks.append(str(rng.choice(other["item_id"])))
            for step, item_id in enumerate(picks):
                price = float(articles.loc[articles["item_id"].eq(item_id), "list_price"].iloc[0])
                rows.append(
                    {
                        "user_id": f"syn-user-{user:03d}",
                        "item_id": item_id,
                        "price": price,
                        "date": f"2024-01-{(step % 27) + 1:02d}",
                    }
                )
        return pd.DataFrame(rows)


class KaggleHMSource(PurchaseHistorySource):
    """Maps the competition files once they are on disk.

    Downloading is a separate call, `download_kaggle`, and it refuses unless
    `KAGGLE_USERNAME`, `KAGGLE_KEY`, and `FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD=1`
    are all set. This class does not open a socket when it reads a folder.
    """

    name = "kaggle_hm"
    COMPETITION = "h-and-m-personalized-fashion-recommendations"

    def __init__(self, folder: Path) -> None:
        self.folder = Path(folder)

    def articles(self) -> pd.DataFrame:
        path = self.folder / "articles.csv"
        raw = pd.read_csv(path, dtype={"article_id": str})
        frame = pd.DataFrame(
            {
                "item_id": raw["article_id"].astype(str),
                "category": raw["product_type_name"].fillna("unknown").str.lower(),
                "color": raw["colour_group_name"].fillna("").str.lower() if "colour_group_name" in raw.columns else "",
                "list_price": pd.NA,
                "fit_rate": pd.NA,
            }
        )
        return frame

    def transactions(self) -> pd.DataFrame:
        path = self.folder / "transactions_train.csv"
        raw = pd.read_csv(path, dtype={"article_id": str, "customer_id": str})
        return pd.DataFrame(
            {
                "user_id": raw["customer_id"].astype(str),
                "item_id": raw["article_id"].astype(str),
                "price": raw["price"],
                "date": raw["t_dat"],
            }
        )


def download_kaggle(destination: Path) -> Path:
    """Blocked by default.

    Neel still has to accept the competition rules in a browser. A key alone
    does not grant the file. This function is the env-var path; the build
    does not call it.
    """
    settings = load_settings()
    if not settings.allow_kaggle_download:
        raise HMDownloadBlocked(
            "H&M download is blocked. Set KAGGLE_USERNAME, KAGGLE_KEY, and "
            "FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD=1 after accepting the Kaggle "
            "competition rules. This repo ships synthetic fixtures instead."
        )
    if not settings.kaggle_username or not settings.kaggle_key:
        raise HMDownloadBlocked(
            "KAGGLE_USERNAME and KAGGLE_KEY are missing. Create a Kaggle API token "
            "and export both. Do not commit them."
        )
    destination.mkdir(parents=True, exist_ok=True)
    # Imported here so CI does not need the Kaggle client.
    from kaggle.api.kaggle_api_extended import KaggleApi

    os.environ["KAGGLE_USERNAME"] = settings.kaggle_username
    os.environ["KAGGLE_KEY"] = settings.kaggle_key
    api = KaggleApi()
    api.authenticate()
    api.competition_download_files(KaggleHMSource.COMPETITION, path=str(destination), quiet=False)
    return destination
