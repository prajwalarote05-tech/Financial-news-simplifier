# FINNEWS AI — Financial News Simplifier 🚀

**FINNEWS AI** is a modern, production-ready full-stack web application designed to democratize financial literacy. It fetches the latest financial and business news from global press outlets and converts complex financial jargon, earnings reports, central bank policies, and economic indicators into plain, beginner-friendly explanations using an LLM.

---

## 🌟 Key Features

- **⚡ Real-Time Financial News Fetching**: Pulls business, stock market, technology, and economic news using [NewsAPI](https://newsapi.org).
- **🧠 AI Jargon Simplifier**: Uses **Groq API** with `llama-3.3-70b-versatile` to produce:
  - Simple 2-3 sentence summaries.
  - Bulleted main takeaways.
  - "Why It Matters" real-world impact explanations.
  - Financial term definitions (Jargon Buster).
- **📊 Real-Time Dashboard Statistics**: Live counters showing total articles fetched, AI simplified, news sources count, and last update timestamp.
- **🔍 Instant Search & Category Filtering**: Filter by *Stock Market*, *Economy*, *Technology*, *Business*, and *Global Markets* or search with live keyword debouncing.
- **🎨 Premium Fintech UI**: Sleek dark dashboard with glassmorphism, responsive mobile-first layout, micro-animations, skeleton loaders, and **Dark/Light Theme Toggle**.
- **📖 Article Detail Modal**: Full breakdown view with interactive jargon definitions and direct links to original articles.
- **🔄 Robust Fallback Logic**: Full-stack design gracefully functions out-of-the-box even prior to API key configuration or during API rate limits.
- **🛡️ Exclusively Secure**: Keeps API keys strictly server-side inside `.env`. Never exposes credentials to frontend code.

---

## 🏗️ Architecture Overview

```
User (Browser)
    │
    ▼
Frontend (Vanilla JS / Modern CSS3)
    │
    ▼  (REST API / CORS)
FastAPI Backend (Python 3.12+)
   ├── Services
   │    ├── News Service ──► NewsAPI (v2/top-headlines)
   │    └── AI Service   ──► Groq API (Llama 3.3 70B)
   └── Routes
        ├── GET  /api/health
        ├── GET  /api/news
        ├── POST /api/summarize
        └── GET  /api/financial-news
```

---

## 📁 Repository Structure

```
Financial News Simplifier/
├── .env.example
├── .gitignore
├── README.md
├── backend/
│   ├── main.py                # FastAPI entry point & CORS configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   ├── .env                   # Local environment keys (gitignored)
│   ├── routes/
│   │   ├── health.py          # GET /api/health
│   │   ├── news.py            # GET /api/news & GET /api/financial-news
│   │   └── summarize.py       # POST /api/summarize
│   ├── services/
│   │   ├── news_service.py    # NewsAPI client with deduplication & fallback
│   │   └── ai_service.py      # Groq Llama 3.3 70B summarizer & fallback
│   ├── models/
│   │   └── schemas.py         # Pydantic data schemas & request validation
│   └── utils/
│       └── config.py          # Environment settings loader
└── frontend/
    ├── index.html             # Dashboard UI
    ├── about.html             # System architecture & documentation page
    ├── css/
    │   └── style.css          # Modern Fintech Design System
    └── js/
        ├── config.js          # Configurable API base URL settings
        ├── api.js             # Async REST API client
        ├── ui.js              # DOM rendering, cards, skeletons, modal & toasts
        └── app.js             # Event wiring & state manager
```

---

## ⚙️ Prerequisites

- **Python**: 3.10+ (Recommended: Python 3.12+)
- **API Keys** *(Optional for basic demo, recommended for live data)*:
  - [NewsAPI Key](https://newsapi.org)
  - [Groq API Key](https://console.groq.com)

---

## 🚀 Local Setup & Installation

### 1. Clone & Set Up Directory
```bash
cd "Financial News Simplifier"
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` inside the `backend/` directory or project root:

```bash
cp .env.example backend/.env
```

Open `backend/.env` and add your API keys:
```env
NEWS_API_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
CORS_ORIGINS=*
```

### 3. Install Backend Dependencies
Create a virtual environment and install dependencies:

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. Run the Application

Execute the FastAPI server with Uvicorn:

```bash
uvicorn backend.main:app --reload --port 8000
```

Once started:
- 🌐 **Web App Dashboard**: Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📘 **Interactive API Docs (Swagger)**: Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📖 **ReDoc API Documentation**: Visit [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints

### 1. `GET /api/health`
Returns system operational status and configuration verification.
```json
{
  "status": "healthy",
  "service": "FINNEWS AI",
  "version": "1.0.0",
  "news_api_configured": true,
  "groq_api_configured": true
}
```

### 2. `GET /api/news`
Query parameters: `category` (*Stock Market, Economy, Technology, Business, Global Markets*), `search`.
Fetches raw articles from NewsAPI with duplicate filtering.

### 3. `POST /api/summarize`
Request body:
```json
{
  "title": "Nvidia Beats Revenue Forecasts on AI Surge",
  "content": "Nvidia posted $30B quarterly revenue driven by data center chips...",
  "description": "Nvidia quarterly results exceed Wall Street expectations."
}
```
Returns structured JSON:
```json
{
  "success": true,
  "summary": "Nvidia earned $30 billion last quarter as companies rushed to buy AI chips.",
  "key_points": [
    "Revenue surged 122% year-over-year to $30 billion.",
    "Data Center chips accounted for $26.3 billion.",
    "Gross margin expanded to 75.1%."
  ],
  "why_it_matters": "Nvidia's rapid growth indicates that tech giants are investing heavily in AI infrastructure.",
  "terms": [
    {
      "term": "Gross Margin",
      "meaning": "The percentage of sales revenue retained after paying production costs."
    }
  ]
}
```

### 4. `GET /api/financial-news`
Combined endpoint: Fetches news, selects top articles, generates AI simplified insights concurrently, and returns live dashboard stats.

---

## 🌐 Production Deployment

### Frontend (e.g., Vercel / Netlify)
1. Deploy the `frontend/` folder as a static site.
2. In `frontend/js/config.js` or through environment scripts, point `window.FINNEWS_CONFIG.API_BASE_URL` to your production backend URL (e.g., `https://your-backend-api.onrender.com/api`).

### Backend (e.g., Render, Railway, Fly.io, AWS)
1. Set Python start command:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
2. Set environment variables on host:
   - `NEWS_API_KEY`
   - `GROQ_API_KEY`
   - `CORS_ORIGINS` (your frontend production domain)

---

## 🛡️ License & Disclaimer

FinNews AI is provided for educational and informational purposes only and does not constitute financial, investment, legal, or tax advice.
