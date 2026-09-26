import logging
import time
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.utils.config import settings
from backend.models.schemas import Article, NewsResponse

logger = logging.getLogger("finnews.news_service")

# In-memory cache for news responses to minimize external API hits
NEWS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

# High-quality real-world financial articles fallback dataset when API key is unconfigured or rate-limited
FALLBACK_ARTICLES: List[Dict[str, Any]] = [
    {
        "title": "Federal Reserve Holds Interest Rates Steady, Hints at Inflation Trends",
        "description": "The Federal Reserve kept key interest rates unchanged at 5.25%-5.50% while signaling that further economic data is needed before rate cuts.",
        "content": "WASHINGTON — The Federal Reserve maintained its benchmark interest rate at a 23-year high during its latest policy meeting. Central bank officials emphasized that inflation has eased over the past year but remains above the 2% target. Chairman Jerome Powell stated that the FOMC needs greater confidence that inflation is moving sustainably toward 2% before initiating rate reductions. Financial markets reacted with cautious optimism as treasury yields dipped slightly and major stock indices traded sideways.",
        "source": "Wall Street Journal",
        "publishedAt": "2026-09-26T14:30:00Z",
        "url": "https://www.wsj.com/economy/central-banking/fed-interest-rates-decision",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80",
        "category": "Economy"
    },
    {
        "title": "Nvidia Beats Q3 Revenue Expectations as Global Demand for AI Chips Soars",
        "description": "Semiconductor giant Nvidia posted record quarterly revenue driven by immense enterprise demand for data center H100 and Blackwell AI GPUs.",
        "content": "SANTA CLARA, Calif. — Semiconductor leader Nvidia announced quarterly revenue of $30.0 billion, up 122% year-over-year, significantly outperforming Wall Street estimates. Growth was spearheaded by its Data Center division, which logged $26.3 billion in revenue. CEO Jensen Huang noted that computing demand has reached a tipping point, with cloud providers and enterprise software firms expanding AI infrastructure rapidly. Nvidia's gross margins expanded to 75.1%, solidifying its market dominance.",
        "source": "Bloomberg",
        "publishedAt": "2026-09-26T12:15:00Z",
        "url": "https://www.bloomberg.com/news/articles/nvidia-earnings-ai-chips-demand",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "category": "Technology"
    },
    {
        "title": "S&P 500 Touches All-Time High Powered by Tech Surge and Strong Consumer Data",
        "description": "U.S. stock benchmark S&P 500 reached a record high as technology shares rallied and consumer spending figures exceeded economist projections.",
        "content": "NEW YORK — U.S. equities surged on Friday, pushing the S&P 500 to a new record high. The rally was broad-based, led by megacap technology firms alongside retail sector gains following robust consumer spending reports. Retail sales increased 0.4% last month, indicating consumer resilience despite elevated borrowing costs. Analysts noted that earnings growth across non-tech sectors is beginning to broaden the market rally.",
        "source": "CNBC",
        "publishedAt": "2026-09-26T10:00:00Z",
        "url": "https://www.cnbc.com/markets/sp500-all-time-high-tech-rally",
        "image": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=800&q=80",
        "category": "Stock Market"
    },
    {
        "title": "Global Oil Prices Drop 3% Following OPEC+ Supply Guidance Adjustments",
        "description": "Brent Crude fell below $75 per barrel after OPEC+ members signaled plans to gradually unwind voluntary production cuts starting next quarter.",
        "content": "LONDON — Crude oil prices sank on international exchanges as energy traders weighed signals from OPEC+ regarding increased crude production later this year. Brent crude futures dropped $2.30 to $73.80 a barrel, while West Texas Intermediate (WTI) traded around $70.10. Energy analysts cited concerns over slowing demand growth in key Asian manufacturing hubs alongside rising non-OPEC crude supplies from the U.S., Guyana, and Brazil.",
        "source": "Reuters",
        "publishedAt": "2026-09-26T08:45:00Z",
        "url": "https://www.reuters.com/business/energy/oil-prices-drop-opec-supply-guidance",
        "image": "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?auto=format&fit=crop&w=800&q=80",
        "category": "Global Markets"
    },
    {
        "title": "U.S. Inflation Cools to 2.5%, Opening Door for Monetary Easing",
        "description": "The Consumer Price Index (CPI) cooled to its lowest annual rate in three years, providing relief for consumers and clear runway for interest rate adjustments.",
        "content": "WASHINGTON — The U.S. Consumer Price Index rose 2.5% on an annual basis last month, down from 2.9% in the prior month, according to the Bureau of Labor Statistics. Core CPI, which excludes volatile food and energy components, increased 0.2% month-over-month. Housing costs remained the single largest contributor to headline inflation, though shelter price growth showed signs of deceleration. Economists project that lower shelter and vehicle inflation will keep price growth tame.",
        "source": "Financial Times",
        "publishedAt": "2026-09-25T16:20:00Z",
        "url": "https://www.ft.com/content/us-cpi-inflation-cooling-fed-rates",
        "image": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80",
        "category": "Economy"
    },
    {
        "title": "Commercial Real Estate Markets Face Refinancing Pressure Amid High Yields",
        "description": "Regional banks and property developers prepare for significant loan maturities as debt costs remain elevated compared to historical averages.",
        "content": "CHICAGO — Property investors and regional financial institutions are navigating a heavy schedule of commercial mortgage renewals. Over $900 billion in debt backed by office buildings, shopping centers, and industrial facilities comes due this year. Property valuations in major metropolitan office towers have adjusted downward by 20% to 35% since 2022, prompting lenders to demand additional equity upfront before extending credit terms.",
        "source": "MarketWatch",
        "publishedAt": "2026-09-25T11:10:00Z",
        "url": "https://www.marketwatch.com/story/commercial-real-estate-refinancing-pressure",
        "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "category": "Business"
    },
    {
        "title": "Asian Tech Stocks Rally on Easing Central Bank Liquidity Policies",
        "description": "Markets in Tokyo, Seoul, and Hong Kong gained momentum as central banks moved to bolster liquidity and lower reserve requirements.",
        "content": "TOKYO — Stock markets across Asia-Pacific registered strong gains on Thursday. Japan's Nikkei 225 surged 1.8% while Hong Kong's Hang Seng Index climbed 2.2%. Market sentiment was buoyed by central bank measures aimed at boosting credit flow to small and medium enterprises. Technology hardware manufacturers and semiconductor suppliers led trading volumes.",
        "source": "Nikkei Asia",
        "publishedAt": "2026-09-25T07:30:00Z",
        "url": "https://asia.nikkei.com/Markets/Equities/Asian-tech-stocks-rally-liquidity",
        "image": "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?auto=format&fit=crop&w=800&q=80",
        "category": "Global Markets"
    }
]

def map_category(title: str, description: str) -> str:
    """Helper to categorize articles based on keywords."""
    text = f"{title} {description}".lower()
    if any(k in text for k in ["stock", "s&p", "dow", "nasdaq", "share", "equity", "rally", "dividend", "earnings"]):
        return "Stock Market"
    elif any(k in text for k in ["fed", "inflation", "cpi", "rate", "interest", "central bank", "gdp", "treasury"]):
        return "Economy"
    elif any(k in text for k in ["ai", "chip", "nvidia", "tech", "apple", "microsoft", "google", "software", "semiconductor"]):
        return "Technology"
    elif any(k in text for k in ["global", "asia", "europe", "oil", "brent", "opec", "forex", "china"]):
        return "Global Markets"
    else:
        return "Business"

def remove_duplicates(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out duplicate or very similar titles."""
    seen_titles = set()
    unique_articles = []
    for art in articles:
        # Simple title normalization
        norm_title = "".join(e for e in art.get("title", "").lower() if e.isalnum())
        if not norm_title or norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)
        unique_articles.append(art)
    return unique_articles

async def fetch_financial_news(category: Optional[str] = None, search: Optional[str] = None) -> NewsResponse:
    """
    Fetches latest financial/business news from NewsAPI.
    If NEWS_API_KEY is not configured or request fails, falls back gracefully to realistic financial news dataset.
    Uses in-memory cache to prevent duplicate external requests.
    """
    cache_key = f"{category or 'all'}:{search or ''}"
    now = time.time()

    if cache_key in NEWS_CACHE:
        entry = NEWS_CACHE[cache_key]
        if now - entry["timestamp"] < CACHE_TTL_SECONDS:
            logger.info(f"Serving news from cache for key: {cache_key}")
            return entry["data"]

    api_key = settings.NEWS_API_KEY

    # Check if key is available
    if not api_key or api_key == "your_newsapi_key_here":
        logger.info("NewsAPI key not configured. Utilizing high-quality fallback financial dataset.")
        filtered = FALLBACK_ARTICLES
        if category and category.lower() != "all":
            filtered = [a for a in filtered if a.get("category", "").lower() == category.lower()]
        if search:
            q = search.lower()
            filtered = [a for a in filtered if q in a.get("title", "").lower() or q in a.get("description", "").lower()]
        
        articles_objs = [Article(**art) for art in filtered]
        return NewsResponse(
            success=True,
            total_results=len(articles_objs),
            articles=articles_objs,
            is_fallback=True
        )

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "category": "business",
        "language": "en",
        "pageSize": settings.MAX_ARTICLES_TO_FETCH
    }
    
    if search:
        # Use everything endpoint if specific query is provided
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": api_key,
            "q": f"finance OR stock OR economy OR business {search}",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": settings.MAX_ARTICLES_TO_FETCH
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)
            
            if res.status_code != 200:
                logger.warning(f"NewsAPI returned status {res.status_code}: {res.text}. Falling back.")
                return _get_fallback_response(category, search)

            data = res.json()
            raw_articles = data.get("articles", [])
            
            cleaned_articles: List[Article] = []
            for art in raw_articles:
                title = art.get("title", "")
                # Skip removed or empty articles
                if not title or title == "[Removed]" or not art.get("url"):
                    continue

                source_name = art.get("source", {}).get("name") if isinstance(art.get("source"), dict) else "Financial News"
                desc = art.get("description") or ""
                content = art.get("content") or desc
                pub_at = art.get("publishedAt") or datetime.utcnow().isoformat() + "Z"
                img = art.get("urlToImage")
                
                # Assign intelligent category
                cat = map_category(title, desc)
                
                cleaned_articles.append(Article(
                    title=title,
                    description=desc,
                    content=content,
                    source=source_name or "Financial Press",
                    publishedAt=pub_at,
                    url=art.get("url"),
                    image=img if img and img.startswith("http") else None,
                    category=cat
                ))

            # Deduplicate by title
            unique_articles_dict = remove_duplicates([a.model_dump() for a in cleaned_articles])
            final_articles = [Article(**a) for a in unique_articles_dict]

            # Apply category filter if passed
            if category and category.lower() != "all":
                final_articles = [a for a in final_articles if a.category.lower() == category.lower()]

            res_obj = NewsResponse(
                success=True,
                total_results=len(final_articles),
                articles=final_articles,
                is_fallback=False
            )
            NEWS_CACHE[cache_key] = {"timestamp": now, "data": res_obj}
            return res_obj

    except Exception as e:
        logger.error(f"Error fetching news from NewsAPI: {str(e)}")
        return _get_fallback_response(category, search)

def _get_fallback_response(category: Optional[str] = None, search: Optional[str] = None) -> NewsResponse:
    filtered = FALLBACK_ARTICLES
    if category and category.lower() != "all":
        filtered = [a for a in filtered if a.get("category", "").lower() == category.lower()]
    if search:
        q = search.lower()
        filtered = [a for a in filtered if q in a.get("title", "").lower() or q in a.get("description", "").lower()]
    
    articles_objs = [Article(**art) for art in filtered]
    return NewsResponse(
        success=True,
        total_results=len(articles_objs),
        articles=articles_objs,
        is_fallback=True
    )
