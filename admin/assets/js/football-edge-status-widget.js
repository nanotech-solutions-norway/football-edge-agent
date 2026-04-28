/* Football Edge / Atlas — Read-Only Status Widget */
(function () {
  "use strict";

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  function setBadge(id, state, text) {
    const element = document.getElementById(id);
    if (!element) return;
    element.textContent = text;
    element.classList.remove("fe-badge-ok", "fe-badge-warning", "fe-badge-error");
    element.classList.add(`fe-badge-${state}`);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderCompetitions(payload) {
    const list = document.getElementById("fe-competitions-list");
    if (!list) return;
    list.innerHTML = "";

    const rows = Array.isArray(payload.data) ? payload.data : [];
    rows.forEach((competition) => {
      const row = document.createElement("div");
      row.className = "fe-competition-row";
      row.innerHTML = `
        <div>
          <strong>${escapeHtml(competition.display_name || "Unknown competition")}</strong>
          <span>${escapeHtml(competition.country || "")}</span>
        </div>
        <code>${escapeHtml(competition.internal_key || "")}</code>
      `;
      list.appendChild(row);
    });
  }

  async function loadFootballEdgeStatus() {
    setBadge("fe-api-status", "warning", "Loading");
    setBadge("fe-safety-status", "warning", "Loading");
    setText("fe-error-message", "");

    try {
      const snapshot = await window.FootballEdgeApi.getDashboardSnapshot();
      setBadge("fe-api-status", "ok", "Online");
      setText("fe-last-updated", new Date(snapshot.generatedAt).toLocaleString());
      setText("fe-competition-count", String(snapshot.competitions.count));
      renderCompetitions(snapshot.competitions);

      const model = snapshot.activeModel.data || {};
      setText("fe-model-version", model.version_key || "Not available");
      setText("fe-model-name", model.model_name || "Not available");
      setText("fe-model-type", model.model_type || "Not available");

      const safetyPayload = snapshot.safetyState || {};
      const control = safetyPayload.auto_betting_control || {};
      const safe = safetyPayload.required_safe_state_ok === true;
      setBadge("fe-safety-status", safe ? "ok" : "error", safe ? "Locked dry-run" : "Unsafe");
      setText("fe-real-betting-status", safetyPayload.real_betting_status || "Unknown");
      setText("fe-auto-betting-enabled", String(control.enabled));
      setText("fe-dry-run", String(control.dry_run));
      setText("fe-provider-name", String(control.provider_name || "none"));
      setText("fe-review-flags", [
        `Legal: ${String(control.legal_review_completed)}`,
        `Compliance: ${String(control.compliance_review_completed)}`,
        `Risk: ${String(control.risk_review_completed)}`
      ].join(" | "));
    } catch (error) {
      setBadge("fe-api-status", "error", "Offline/error");
      setBadge("fe-safety-status", "error", "Not verified");
      setText("fe-error-message", error.message || "Unknown API error");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const refreshButton = document.getElementById("fe-refresh-button");
    if (refreshButton) refreshButton.addEventListener("click", loadFootballEdgeStatus);
    loadFootballEdgeStatus();
  });

  window.loadFootballEdgeStatus = loadFootballEdgeStatus;
})();
