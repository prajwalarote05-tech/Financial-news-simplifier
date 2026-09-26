from typing import List, Optional
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(..., description="Article headline")
    description: Optional[str] = Field(default="", description="Short snippet/summary")
    content: Optional[str] = Field(default="", description="Full or partial article content")
    source: str = Field(default="Financial News", description="Publisher / source name")
    publishedAt: str = Field(..., description="ISO publication timestamp")
    url: str = Field(..., description="Link to full original article")
    image: Optional[str] = Field(default=None, description="Featured image URL")
    category: Optional[str] = Field(default="Business", description="Topic category")

class NewsResponse(BaseModel):
    success: bool = True
    total_results: int = 0
    articles: List[Article] = []
    error: Optional[str] = None
    is_fallback: bool = False

class TermExplanation(BaseModel):
    term: str = Field(..., description="Financial term or acronym")
    meaning: str = Field(..., description="Simple 1-sentence definition")

class SummarizeRequest(BaseModel):
    title: str = Field(..., description="Article headline")
    content: Optional[str] = Field(default="", description="Article content or snippet")
    description: Optional[str] = Field(default="", description="Article summary description")
    url: Optional[str] = Field(default="", description="Optional article source link")

class SummarizeResponse(BaseModel):
    success: bool = True
    summary: str = Field(..., description="Simple beginner-friendly summary of the article")
    key_points: List[str] = Field(default_factory=list, description="3-4 main takeaway bullet points")
    why_it_matters: str = Field(..., description="Explanation of real-world impact for non-experts")
    terms: List[TermExplanation] = Field(default_factory=list, description="Glossary of financial jargon explained")
    error: Optional[str] = None

class SimplifiedArticle(Article):
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    why_it_matters: Optional[str] = None
    terms: Optional[List[TermExplanation]] = None
    simplified: bool = False

class CombinedNewsResponse(BaseModel):
    success: bool = True
    total_fetched: int = 0
    total_simplified: int = 0
    sources_count: int = 0
    last_updated: str = ""
    articles: List[SimplifiedArticle] = []
    error: Optional[str] = None
    notice: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "FINNEWS AI"
    version: str = "1.0.0"
    news_api_configured: bool = False
    groq_api_configured: bool = False
