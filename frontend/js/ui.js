/**
 * FINNEWS AI — UI Renderer & Component Module
 * Manages DOM updates, article cards, skeletons, detail modals, themes, and toasts.
 */

const UI = (function () {
  // Fallback financial background images for broken external image links
  const FALLBACK_IMAGES = [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80'
  ];

  function getFallbackImage(index = 0) {
    return FALLBACK_IMAGES[index % FALLBACK_IMAGES.length];
  }

  function formatDate(isoString) {
    if (!isoString) return 'Recent';
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) return 'Recent';
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch (e) {
      return 'Recent';
    }
  }

  function renderSkeletons(container, count = 6) {
    container.innerHTML = Array(count)
      .fill(0)
      .map(
        () => `
      <div class="skeleton-card">
        <div class="skeleton-image"></div>
        <div class="skeleton-content">
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-100"></div>
          <div class="skeleton-line w-80"></div>
          <div class="skeleton-line h-60"></div>
          <div class="skeleton-line w-40"></div>
        </div>
      </div>
    `
      )
      .join('');
  }

  function renderStats(data) {
    const fetchedEl = document.getElementById('stat-fetched');
    const simplifiedEl = document.getElementById('stat-simplified');
    const sourcesEl = document.getElementById('stat-sources');
    const updatedEl = document.getElementById('stat-updated');

    if (fetchedEl) fetchedEl.textContent = data.total_fetched || 0;
    if (simplifiedEl) simplifiedEl.textContent = data.total_simplified || 0;
    if (sourcesEl) sourcesEl.textContent = data.sources_count || 0;
    if (updatedEl) updatedEl.textContent = data.last_updated || 'Just now';
  }

  function renderNotice(noticeText) {
    const noticeEl = document.getElementById('notice-container');
    if (!noticeEl) return;
    if (noticeText) {
      noticeEl.style.display = 'flex';
      noticeEl.innerHTML = `<i class="fa-solid fa-circle-info"></i> <span>${noticeText}</span>`;
    } else {
      noticeEl.style.display = 'none';
      noticeEl.innerHTML = '';
    }
  }

  function renderArticles(container, articles, onArticleClick) {
    if (!articles || articles.length === 0) {
      renderEmptyState(container, 'No Financial News Found', 'Try adjusting your search keywords or switching category filters.');
      return;
    }

    container.innerHTML = articles
      .map((article, idx) => {
        const imageSrc = article.image || getFallbackImage(idx);
        const category = article.category || 'Business';
        const formattedDate = formatDate(article.publishedAt);
        const keyPointsList = (article.key_points || [])
          .slice(0, 3)
          .map((pt) => `<li>${pt}</li>`)
          .join('');

        const termsPills = (article.terms || [])
          .slice(0, 3)
          .map((t) => `<span class="term-tag">${t.term}</span>`)
          .join('');

        return `
        <article class="news-card" data-index="${idx}">
          <div class="card-image-wrapper">
            <img 
              src="${imageSrc}" 
              alt="${article.title}" 
              class="card-image"
              loading="lazy"
              onerror="this.onerror=null; this.src='${getFallbackImage(idx)}';"
            />
            <span class="card-category-badge">${category}</span>
          </div>

          <div class="card-body">
            <div class="card-meta">
              <span class="card-source"><i class="fa-solid fa-newspaper"></i> ${article.source}</span>
              <span class="card-date"><i class="fa-regular fa-clock"></i> ${formattedDate}</span>
            </div>

            <h3 class="card-title">${article.title}</h3>

            <div class="simplified-box">
              <div class="simplified-header">
                <i class="fa-solid fa-wand-magic-sparkles"></i> Simplified Insight
              </div>
              <p class="simplified-text">${article.summary || article.description || 'AI simplification in progress...'}</p>
            </div>

            ${
              keyPointsList
                ? `
              <ul class="key-points-list">
                ${keyPointsList}
              </ul>
            `
                : ''
            }

            ${
              article.why_it_matters
                ? `
              <div class="card-why-matters">
                <strong><i class="fa-solid fa-bullseye"></i> Why It Matters:</strong> ${article.why_it_matters}
              </div>
            `
                : ''
            }

            ${
              termsPills
                ? `
              <div class="terms-container">
                ${termsPills}
              </div>
            `
                : ''
            }

            <div class="card-footer">
              <button class="btn-secondary btn-details" data-index="${idx}">
                <i class="fa-solid fa-expand"></i> Details & Glossary
              </button>
              <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="btn-link">
                Read Original Article <i class="fa-solid fa-arrow-up-right-from-square"></i>
              </a>
            </div>
          </div>
        </article>
      `;
      })
      .join('');

    // Attach click listeners to cards / details buttons
    container.querySelectorAll('.btn-details, .news-card').forEach((el) => {
      el.addEventListener('click', (e) => {
        // Prevent trigger if clicking directly on external original article link
        if (e.target.closest('.btn-link')) return;

        const cardEl = e.target.closest('.news-card');
        if (cardEl) {
          const index = parseInt(cardEl.getAttribute('data-index'), 10);
          if (articles[index] && typeof onArticleClick === 'function') {
            onArticleClick(articles[index]);
          }
        }
      });
    });
  }

  function renderEmptyState(container, title, message) {
    container.innerHTML = `
      <div class="state-container">
        <div class="state-icon"><i class="fa-solid fa-newspaper"></i></div>
        <h3 class="state-title">${title}</h3>
        <p class="state-desc">${message}</p>
        <button class="btn-primary" onclick="window.resetFilters && window.resetFilters()">
          <i class="fa-solid fa-rotate-left"></i> Reset Filters
        </button>
      </div>
    `;
  }

  function renderErrorState(container, errorMessage, onRetry) {
    container.innerHTML = `
      <div class="state-container">
        <div class="state-icon" style="color: #ef4444;"><i class="fa-solid fa-triangle-exclamation"></i></div>
        <h3 class="state-title">Unable to Load News</h3>
        <p class="state-desc">${errorMessage || 'News service is temporarily unavailable. Please try again.'}</p>
        <button class="btn-primary" id="btn-retry-error">
          <i class="fa-solid fa-rotate-right"></i> Try Again
        </button>
      </div>
    `;

    const retryBtn = container.querySelector('#btn-retry-error');
    if (retryBtn && typeof onRetry === 'function') {
      retryBtn.addEventListener('click', onRetry);
    }
  }

  function openArticleModal(article) {
    const modalOverlay = document.getElementById('article-modal');
    if (!modalOverlay) return;

    document.getElementById('modal-title').textContent = article.title || 'Financial Insight';
    document.getElementById('modal-source').textContent = article.source || 'News Source';
    document.getElementById('modal-date').textContent = formatDate(article.publishedAt);
    document.getElementById('modal-category').textContent = article.category || 'Financial News';
    document.getElementById('modal-summary').textContent = article.summary || article.description || 'N/A';
    document.getElementById('modal-why-it-matters').textContent = article.why_it_matters || 'Understanding this update provides clarity on broader financial trends.';
    document.getElementById('modal-original-url').href = article.url || '#';

    // Render key points in modal
    const keyPointsUl = document.getElementById('modal-key-points');
    if (keyPointsUl) {
      if (article.key_points && article.key_points.length > 0) {
        keyPointsUl.innerHTML = article.key_points.map((pt) => `<li>${pt}</li>`).join('');
      } else {
        keyPointsUl.innerHTML = '<li>Key market breakdown not available for this article.</li>';
      }
    }

    // Render terms in modal
    const termsGrid = document.getElementById('modal-terms-grid');
    if (termsGrid) {
      if (article.terms && article.terms.length > 0) {
        termsGrid.innerHTML = article.terms
          .map(
            (t) => `
          <div class="term-box">
            <div class="term-box-title"><i class="fa-solid fa-book-bookmark"></i> ${t.term}</div>
            <div class="term-box-desc">${t.meaning}</div>
          </div>
        `
          )
          .join('');
      } else {
        termsGrid.innerHTML = `
          <div class="term-box">
            <div class="term-box-title"><i class="fa-solid fa-book-bookmark"></i> Financial News</div>
            <div class="term-box-desc">Standard financial coverage for market participants.</div>
          </div>
        `;
      }
    }

    modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeArticleModal() {
    const modalOverlay = document.getElementById('article-modal');
    if (modalOverlay) {
      modalOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    let icon = '<i class="fa-solid fa-circle-info" style="color:#3b82f6;"></i>';
    if (type === 'success') icon = '<i class="fa-solid fa-circle-check" style="color:#10b981;"></i>';
    if (type === 'error') icon = '<i class="fa-solid fa-circle-xmark" style="color:#ef4444;"></i>';

    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function initTheme() {
    const savedTheme = localStorage.getItem('finnews_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('finnews_theme', newTheme);
    updateThemeIcon(newTheme);
    showToast(`Switched to ${newTheme.toUpperCase()} theme`, 'info');
  }

  function updateThemeIcon(theme) {
    const themeBtn = document.getElementById('btn-theme-toggle');
    if (themeBtn) {
      themeBtn.innerHTML = theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
      themeBtn.setAttribute('title', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }

  return {
    renderSkeletons,
    renderStats,
    renderNotice,
    renderArticles,
    renderEmptyState,
    renderErrorState,
    openArticleModal,
    closeArticleModal,
    showToast,
    initTheme,
    toggleTheme,
  };
})();

window.UI = UI;
