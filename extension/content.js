/* Demo-page reader. The attributes match fit_finder.pageparse.
   The API origin comes from the popup override, then extension/config.js,
   then the local API when this page itself is on localhost. */
(function () {
  "use strict";

  function product() {
    var node = document.querySelector("article.product");
    if (!node) return null;
    var colors = (node.getAttribute("data-colors") || "")
      .split(",")
      .map(function (part) { return part.trim(); })
      .filter(Boolean);
    var selected = document.querySelector("#size-select option[selected]");
    var current = document.querySelector("#size-select");
    return {
      productId: node.getAttribute("data-product-id"),
      title: (document.querySelector("h1.product-title") || {}).textContent || "",
      category: node.getAttribute("data-category"),
      price: node.getAttribute("data-price"),
      colors: colors,
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

  function localFallback() {
    var host = location.hostname;
    if (host === "localhost" || host === "127.0.0.1") return "http://127.0.0.1:8000";
    return "";
  }

  function resolveApi(done) {
    var configured = (typeof FIT_FINDER_API_BASE === "string" ? FIT_FINDER_API_BASE : "").replace(/\/$/, "");
    function finish(value) {
      done((value || configured || localFallback()).replace(/\/$/, ""));
    }
    try {
      chrome.storage.local.get(["apiBase"], function (stored) {
        finish(stored && stored.apiBase ? String(stored.apiBase) : "");
      });
    } catch (err) {
      finish("");
    }
  }

  function ask(api, page) {
    var size = Number(page.selectedSize);
    render("<p>Asking " + api + " about size " + page.selectedSize + ".</p>");
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
        var local = api.indexOf("127.0.0.1") !== -1 || api.indexOf("localhost") !== -1;
        var copy = local
          ? "The local API is not running. Start it with <code>fit-finder-api</code> on port 8000, then reload this page."
          : "The configured API at <code>" + api + "</code> is not reachable. Nothing on this page was invented as a prediction.";
        render("<p>" + copy + "</p>");
      });
  }

  function load() {
    if (document.getElementById("fit-finder-panel")) return;
    var page = product();
    if (!page) return;
    resolveApi(function (api) {
      if (!api) {
        render("<p>The public API URL is not set. After the free host prints an https origin, put it in <code>extension/config.js</code> and <code>deploy/public.json</code>. The extension does not run on retailer sites.</p>");
        return;
      }
      ask(api, page);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
