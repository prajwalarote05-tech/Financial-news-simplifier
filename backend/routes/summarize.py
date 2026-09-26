from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import SummarizeRequest, SummarizeResponse
from backend.services.ai_service import summarize_financial_article

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse, summary="Simplify Article with Groq AI")
async def summarize_article(payload: SummarizeRequest):
    """
    Takes an article title, content, or description and returns a simplified, beginner-friendly explanation,
    key points, why it matters, and a financial glossary using Groq Llama 3.3 70B.
    """
    if not payload.title or len(payload.title.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article title is required to generate a summary."
        )

    response = await summarize_financial_article(
        title=payload.title,
        content=payload.content or "",
        description=payload.description or ""
    )
    return response
