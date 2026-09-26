/**
 * FINNEWS AI — API Client Module
 * Communicates with FastAPI backend endpoints:
 * - GET /api/health
 * - GET /api/news
 * - GET /api/financial-news
 * - POST /api/summarize
 */

const ApiClient = (function () {
  function getBaseUrl() {
    return window.FINNEWS_CONFIG.API_BASE_URL.replace(/\/$/, '');
  }

  async function request(endpoint, options = {}) {
    const url = `${getBaseUrl()}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { detail: response.statusText };
        }
        throw new Error(errorData.detail || errorData.message || `Server error (${response.status})`);
      }
      return await response.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  }

  return {
    async checkHealth() {
      return request('/health');
    },

    async fetchNews(category = null, search = null) {
      const params = new URLSearchParams();
      if (category && category.toLowerCase() !== 'all') params.append('category', category);
      if (search && search.trim() !== '') params.append('search', search.trim());

      const queryStr = params.toString() ? `?${params.toString()}` : '';
      return request(`/news${queryStr}`);
    },

    async fetchFinancialNewsCombined(category = null, search = null, limit = 6) {
      const params = new URLSearchParams();
      if (category && category.toLowerCase() !== 'all') params.append('category', category);
      if (search && search.trim() !== '') params.append('search', search.trim());
      if (limit) params.append('limit', limit);

      const queryStr = params.toString() ? `?${params.toString()}` : '';
      return request(`/financial-news${queryStr}`);
    },

    async summarizeArticle(title, content, description = '') {
      return request('/summarize', {
        method: 'POST',
        body: JSON.stringify({ title, content, description }),
      });
    },
  };
})();

window.ApiClient = ApiClient;
