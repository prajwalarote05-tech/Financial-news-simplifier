/**
 * FINNEWS AI — Environment & API Configuration
 */

(function () {
  let defaultApiBaseUrl = 'http://127.0.0.1:8000/api';

  // When frontend is served directly by FastAPI
  if (window.location.port === '8000') {
    defaultApiBaseUrl = `${window.location.origin}/api`;
  }

  window.FINNEWS_CONFIG = Object.assign(
    {
      API_BASE_URL: defaultApiBaseUrl,
      DEFAULT_ARTICLE_LIMIT: 6,
      SEARCH_DEBOUNCE_MS: 350,
    },
    window.FINNEWS_CONFIG || {}
  );
})();
