from fastapi import APIRouter
from backend.models.schemas import HealthResponse
from backend.utils.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="Check API Health")
async def health_check():
    """
    Returns API operational status and configuration verification.
    """
    news_configured = bool(settings.NEWS_API_KEY and settings.NEWS_API_KEY != "your_newsapi_key_here")
    groq_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here")
    
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        news_api_configured=news_configured,
        groq_api_configured=groq_configured
    )
