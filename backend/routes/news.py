import asyncio
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Query
from backend.models.schemas import NewsResponse, CombinedNewsResponse, SimplifiedArticle
from backend.services.news_service import fetch_financial_news
from backend.services.ai_service import summarize_financial_article
from backend.utils.config import settings

router = APIRouter()

@router.get("/news", response_model=NewsResponse, summary="Fetch Latest Financial News")
async def get_news(
    category: Optional[str] = Query(default=None, description="Category filter (e.g. Stock Market, Economy, Technology, Business, Global Markets)"),
    search: Optional[str] = Query(default=None, description="Search query string")
):
    """
    Fetches raw latest financial/business news articles from NewsAPI with duplicate filtering.
    """
    response = await fetch_financial_news(category=category, search=search)
    return response

@router.get("/financial-news", response_model=CombinedNewsResponse, summary="Fetch & Simplify Financial News Dashboard Payload")
async def get_financial_news_combined(
    category: Optional[str] = Query(default=None, description="Category filter"),
    search: Optional[str] = Query(default=None, description="Search query"),
    limit: int = Query(default=settings.DEFAULT_SUMMARIZE_COUNT, ge=1, le=15, description="Number of articles to simplify")
):
    """
    Combined endpoint:
    1. Fetches latest relevant financial news.
    2. Selects top articles (default 5-8).
    3. Runs AI simplification concurrently.
    4. Computes real-time statistics (total_fetched, total_simplified, sources_count, last_updated).
    """
    news_res = await fetch_financial_news(category=category, search=search)
    
    if not news_res.success or not news_res.articles:
        return CombinedNewsResponse(
            success=True,
            total_fetched=0,
            total_simplified=0,
            sources_count=0,
            last_updated=datetime.now().strftime("%I:%M %p, %b %d, %Y"),
            articles=[],
            notice="No financial news articles found matching criteria."
        )

    raw_articles = news_res.articles[:limit]
    
    # Run async summarization tasks concurrently for maximum speed
    async def process_single_article(article):
        ai_res = await summarize_financial_article(
            title=article.title,
            content=article.content or article.description or "",
            description=article.description or ""
        )
        return SimplifiedArticle(
            title=article.title,
            description=article.description,
            content=article.content,
            source=article.source,
            publishedAt=article.publishedAt,
            url=article.url,
            image=article.image,
            category=article.category,
            summary=ai_res.summary,
            key_points=ai_res.key_points,
            why_it_matters=ai_res.why_it_matters,
            terms=ai_res.terms,
            simplified=ai_res.success
        )

    tasks = [process_single_article(art) for art in raw_articles]
    simplified_articles: List[SimplifiedArticle] = await asyncio.gather(*tasks)

    # Compute live dashboard stats
    sources = set(art.source for art in news_res.articles)
    simplified_count = sum(1 for art in simplified_articles if art.simplified)
    
    notice_msg = None
    if news_res.is_fallback:
        notice_msg = "Using real-world financial sample dataset. Configure NEWS_API_KEY and GROQ_API_KEY in backend/.env for live API fetching."

    return CombinedNewsResponse(
        success=True,
        total_fetched=len(news_res.articles),
        total_simplified=simplified_count,
        sources_count=len(sources),
        last_updated=datetime.now().strftime("%I:%M %p, %b %d, %Y"),
        articles=simplified_articles,
        notice=notice_msg
    )
