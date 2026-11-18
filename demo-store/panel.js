/* Demo page client. Reads config.json. Does not call a retailer. */
(function () {
  "use strict";

  function product() {
    var node = document.querySelector("article.product");
    if (!node) return null;
    var colors = (node.getAttribute("data-colors") || "")
      .split(",")
      .map(function (part) { return part.trim(); })
      .filter(Boolean);
    var sizes = Array.prototype.map.call(
      document.querySelectorAll("table.size-chart tr[data-size]"),
      function (row) {
        return { size: row.getAttribute("data-size"), text: row.innerText.replace(/\s+/g, " ").trim() };
      }
    );
    var selected = document.querySelector("#size-select option[selected]");
    var current = document.querySelector("#size-select");
    return {
      productId: node.getAttribute("data-product-id"),
      title: (document.querySelector("h1.product-title") || {}).textContent || "",
      category: node.getAttribute("data-category"),
      price: node.getAttribute("data-price"),
      colors: colors,
      sizes: sizes,
      selectedSize: (selected && selected.value) || (current && current.value) || null
    };
  }

  function panel() {
    var existing = document.getElementById("fit-finder-panel");
    if (existing) return existing;
    var node = document.createElement("aside");
    node.id = "fit-finder-panel";
    node.innerHTML = "<h2>fit-finder</h2><p class=\"ff-note\">Demo page. Not a retailer prediction.</p><div id=\"ff-body\">Reading this page…</div>";
    document.body.appendChild(node);
    return node;
  }

  function render(html) {
    panel();
    document.getElementById("ff-body").innerHTML = html;
  }

  function ask(api, page) {
    var size = Number(page.selectedSize);
    var pending = api.indexOf(".onrender.com") !== -1
      ? "<p>The free host sleeps when nobody is calling it. This page is waking the free server (~1 min).</p>"
      : "<p>Asking " + api + " about size " + page.selectedSize + ".</p>";
    render(pending);
    fetch(api + "/predict-size", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: page.category,
        size_index: size,
        source: "demo-store",
        item_id: page.productId
      })
    })
      .then(function (response) {
        if (!response.ok) throw new Error("predict " + response.status);
        return response.json();
      })
      .then(function (prediction) {
        return fetch(api + "/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            category: page.category,
            size_index: prediction.recommended_size,
            limit: 3,
            price: Number(page.price),
            color: page.colors[0] || null
          })
        }).then(function (response) {
          if (!response.ok) throw new Error("recommend " + response.status);
          return response.json().then(function (recs) {
            return { prediction: prediction, recs: recs };
          });
        });
      })
      .then(function (both) {
        var p = both.prediction;
        var items = both.recs.items.map(function (item) {
          return "<li>" + item.item_id + " · fit rate " + Math.round(item.fit_rate * 100) + "%</li>";
        }).join("");
        render(
          "<p class=\"ff-size\">Suggested size <strong>" + p.recommended_size + "</strong></p>" +
          "<p>Ordered " + p.ordered_size + " looks <strong>" + p.fit_class + "</strong> with confidence " +
          Math.round(p.confidence * 100) + "%.</p>" +
          "<p>" + p.size_note + "</p>" +
          "<p class=\"ff-note\">Model " + p.model + ". Colors on this page: " + page.colors.join(", ") +
          ". Price $" + page.price + " is filtered only against an illustrative band.</p>" +
          "<h3>Similar in this category</h3><ul>" + (items || "<li>No catalog rows for this category.</li>") + "</ul>"
        );
        fetch(api + "/events", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event_type: "prediction",
            session_id: "demo-store",
            item_id: page.productId,
            category: page.category,
            arm: "recs"
          })
        }).catch(function () { return null; });
      })
      .catch(function () {
        render("<p>The configured API at <code>" + api + "</code> is not reachable. Nothing on this page was invented as a prediction.</p>");
      });
  }

  function boot(apiBase) {
    var page = product();
    if (!page) return;
    if (document.getElementById("fit-finder-panel")) return;
    var api = (apiBase || "").replace(/\/$/, "");
    if (!api) {
      render("<p>The public API URL is not set. The owner fills <code>deploy/public.json</code> with the free host's https origin after the first deploy. This page does not call a machine on the owner's laptop.</p>");
      return;
    }
    ask(api, page);
  }

  function start() {
    var host = location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      boot("http://127.0.0.1:8000");
      return;
    }
    fetch("config.json", { cache: "no-store" })
      .then(function (response) { return response.ok ? response.json() : {}; })
      .catch(function () { return {}; })
      .then(function (config) { boot(config.apiBase || ""); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
