"""Read the demo-store page contract.

The Chrome extension's content script reads the same attributes. Tests use
this parser so CI does not need a browser. The contract is:

- article.product[data-product-id]
- data-category, data-price, data-colors
- table.size-chart tr[data-size]
- select#size-select option[selected], or the first option

The extension is not allowed to run on retailer hosts. See the manifest test.
"""

from __future__ import annotations

from html.parser import HTMLParser


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.product: dict = {
            "product_id": None,
            "category": None,
            "price": None,
            "colors": [],
            "title": None,
            "sizes": [],
            "selected_size": None,
        }
        self._in_product = False
        self._in_title = False
        self._in_size_chart = False
        self._in_select = False
        self._current_size: dict | None = None
        self._cell_text: list[str] = []
        self._in_cell = False
        self._option_size: str | None = None
        self._option_selected = False

    def handle_starttag(self, tag, attrs):
        attr = {key: value for key, value in attrs}
        classes = set((attr.get("class") or "").split())
        if tag == "article" and "product" in classes:
            self._in_product = True
            self.product["product_id"] = attr.get("data-product-id")
            self.product["category"] = attr.get("data-category")
            self.product["price"] = attr.get("data-price")
            colors = attr.get("data-colors") or ""
            self.product["colors"] = [part.strip() for part in colors.split(",") if part.strip()]
        if tag == "h1" and "product-title" in classes:
            self._in_title = True
        if tag == "table" and "size-chart" in classes:
            self._in_size_chart = True
        if self._in_size_chart and tag == "tr" and attr.get("data-size"):
            self._current_size = {"size": attr["data-size"], "cells": []}
        if self._current_size is not None and tag in {"td", "th"}:
            self._in_cell = True
            self._cell_text = []
        if tag == "select" and attr.get("id") == "size-select":
            self._in_select = True
        if self._in_select and tag == "option":
            self._option_size = attr.get("value")
            self._option_selected = "selected" in attr

    def handle_endtag(self, tag):
        if tag == "h1" and self._in_title:
            self._in_title = False
        if tag == "table" and self._in_size_chart:
            self._in_size_chart = False
        if tag in {"td", "th"} and self._in_cell and self._current_size is not None:
            self._current_size["cells"].append("".join(self._cell_text).strip())
            self._in_cell = False
        if tag == "tr" and self._current_size is not None:
            self.product["sizes"].append(self._current_size)
            self._current_size = None
        if tag == "option" and self._option_size is not None:
            if self._option_selected or self.product["selected_size"] is None:
                if self._option_selected or self.product["selected_size"] is None:
                    if self._option_selected or self.product["selected_size"] is None:
                        self.product["selected_size"] = self._option_size
            if self._option_selected:
                self.product["selected_size"] = self._option_size
            self._option_size = None
            self._option_selected = False
        if tag == "select":
            self._in_select = False
        if tag == "article":
            self._in_product = False

    def handle_data(self, data):
        if self._in_title:
            text = data.strip()
            if text:
                self.product["title"] = text
        if self._in_cell:
            self._cell_text.append(data)


def parse_product_html(html: str) -> dict:
    parser = _Parser()
    parser.feed(html)
    return parser.product
