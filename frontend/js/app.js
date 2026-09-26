/**
 * FINNEWS AI — Main Application Controller
 * Connects API Client with UI Renderer and manages state & events.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    currentCategory: 'All',
    searchQuery: '',
    articles: [],
    isRequestPending: false,
    lastFetchedTime: null,
  };

  // DOM Elements
  const newsGrid = document.getElementById('news-grid');
  const searchInput = document.getElementById('search-input');
  const filterPills = document.querySelectorAll('.filter-pill');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnFetchHero = document.getElementById('btn-fetch-hero');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalOverlay = document.getElementById('article-modal');
  const themeToggleBtn = document.getElementById('btn-theme-toggle');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.getElementById('nav-links');

  // Initialize UI Theme
  UI.initTheme();

  // Load Initial Financial News
  loadFinancialNews();

  // Mobile Menu Toggle
  if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
    });
  }

  // Event Listeners
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', UI.toggleTheme);
  }

  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      if (state.isRequestPending) {
        UI.showToast('News refresh already in progress...', 'info');
        return;
      }
      loadFinancialNews(true);
    });
  }

  if (btnFetchHero) {
    btnFetchHero.addEventListener('click', () => {
      // Scroll smoothly to news section and refresh
      const newsSection = document.getElementById('news-section');
      if (newsSection) {
        newsSection.scrollIntoView({ behavior: 'smooth' });
      }
      if (!state.isRequestPending) {
        loadFinancialNews(true);
      }
    });
  }

  // Search Input Debouncing
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      state.searchQuery = e.target.value.trim();

      searchTimeout = setTimeout(() => {
        loadFinancialNews();
      }, window.FINNEWS_CONFIG.SEARCH_DEBOUNCE_MS || 350);
    });
  }

  // Category Filter Pills
  filterPills.forEach((pill) => {
    pill.addEventListener('click', () => {
      filterPills.forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');

      const category = pill.getAttribute('data-category') || 'All';
      state.currentCategory = category;
      loadFinancialNews();
    });
  });

  // Modal Close Handlers
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', UI.closeArticleModal);
  }

  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        UI.closeArticleModal();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      UI.closeArticleModal();
    }
  });

  // Global reset helper for empty state button
  window.resetFilters = function () {
    state.currentCategory = 'All';
    state.searchQuery = '';
    if (searchInput) searchInput.value = '';

    filterPills.forEach((p) => {
      p.classList.toggle('active', p.getAttribute('data-category') === 'All');
    });

    loadFinancialNews();
  };

  /**
   * Main function to fetch and simplify news
   */
  async function loadFinancialNews(isManualRefresh = false) {
    if (state.isRequestPending) return;

    state.isRequestPending = true;
    updateRefreshButtonState(true);
    UI.renderSkeletons(newsGrid, 6);

    try {
      const data = await ApiClient.fetchFinancialNewsCombined(
        state.currentCategory,
        state.searchQuery,
        window.FINNEWS_CONFIG.DEFAULT_ARTICLE_LIMIT
      );

      state.articles = data.articles || [];

      // Render stats and notices
      UI.renderStats(data);
      UI.renderNotice(data.notice);

      // Render news cards grid
      UI.renderArticles(newsGrid, state.articles, (selectedArticle) => {
        UI.openArticleModal(selectedArticle);
      });

      if (isManualRefresh) {
        UI.showToast('Financial news refreshed successfully!', 'success');
      }
    } catch (err) {
      console.error('Error fetching financial news:', err);
      UI.renderErrorState(
        newsGrid,
        'News service is temporarily unavailable. Please try again.',
        () => loadFinancialNews(true)
      );
      UI.showToast('News service is temporarily unavailable. Please try again.', 'error');
    } finally {
      state.isRequestPending = false;
      updateRefreshButtonState(false);
    }
  }

  function updateRefreshButtonState(isLoading) {
    if (!btnRefresh) return;
    const icon = btnRefresh.querySelector('i');
    if (isLoading) {
      btnRefresh.disabled = true;
      if (icon) icon.className = 'fa-solid fa-arrows-rotate fa-spin';
    } else {
      btnRefresh.disabled = false;
      if (icon) icon.className = 'fa-solid fa-arrows-rotate';
    }
  }
});
