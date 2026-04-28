/* Football Edge / Atlas — Read-Only API Client
 * Scope: read-only API calls only. No credentials. No direct database access.
 */
(function () {
  "use strict";

  const DEFAULT_API_BASE_URL = "/api";

  function normalizeBaseUrl(baseUrl) {
    return String(baseUrl || DEFAULT_API_BASE_URL).replace(/\/+$/, "");
  }

  async function requestJson(path, options = {}) {
    const baseUrl = normalizeBaseUrl(options.baseUrl || window.FOOTBALL_EDGE_API_BASE_URL);
    const url = `${baseUrl}${path}`;

    const response = await fetch(url, {
      method: "GET",
      headers: { "Accept": "application/json" },
      credentials: "omit",
      cache: "no-store"
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      throw new Error(`API returned non-JSON response for ${path}. HTTP ${response.status}`);
    }

    if (!response.ok || payload.status !== "ok") {
      const message = payload && payload.message ? payload.message : `API request failed for ${path}. HTTP ${response.status}`;
      throw new Error(message);
    }

    return payload;
  }

  window.FootballEdgeApi = {
    getHealth(options = {}) { return requestJson("/health", options); },
    getCompetitions(options = {}) { return requestJson("/competitions", options); },
    getActiveModelVersion(options = {}) { return requestJson("/model-version/active", options); },
    getSafetyState(options = {}) { return requestJson("/system/safety-state", options); },
    async getDashboardSnapshot(options = {}) {
      const [health, competitions, activeModel, safetyState] = await Promise.all([
        this.getHealth(options),
        this.getCompetitions(options),
        this.getActiveModelVersion(options),
        this.getSafetyState(options)
      ]);
      return { health, competitions, activeModel, safetyState, generatedAt: new Date().toISOString() };
    }
  };
})();
