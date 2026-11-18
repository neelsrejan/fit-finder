/* Saves an API origin in chrome.storage. Never asks for a secret. */
(function () {
  var input = document.getElementById("api-base");
  var status = document.getElementById("status");
  chrome.storage.local.get(["apiBase"], function (stored) {
    input.value = (stored && stored.apiBase) || "";
  });
  document.getElementById("save").addEventListener("click", function () {
    var value = input.value.trim().replace(/\/$/, "");
    if (value && !/^https:\/\/[a-z0-9.-]+(?::\d+)?$/i.test(value) && !/^http:\/\/(127\.0\.0\.1|localhost)(?::\d+)?$/i.test(value)) {
      status.textContent = "Use an https origin, or http://127.0.0.1:8000 for an offline run.";
      return;
    }
    chrome.storage.local.set({ apiBase: value }, function () {
      status.textContent = value ? "Saved. Reload the demo page." : "Cleared. The extension uses extension/config.js.";
    });
  });
})();
