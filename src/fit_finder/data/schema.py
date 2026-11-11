"""Column names shared by the cleaned review table."""

from __future__ import annotations

FIT_CLASSES = ("small", "fit", "large")

REVIEW_COLUMNS = (
    "source",
    "user_id",
    "item_id",
    "category",
    "size_raw",
    "size_index",
    "fit",
    "rating",
    "height_in",
    "weight_lbs",
    "bust_band",
    "cup",
    "age",
    "body_type",
    "rented_for",
    "review_date",
    "row_id",
)

# Outcomes from the review itself. They are not model inputs.
LEAKY_FIELDS = ("quality", "length", "review_text", "review_summary", "user_name")
