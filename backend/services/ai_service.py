import json
import logging
import re
import time
import hashlib
import httpx
from typing import Dict, Any, List
from backend.utils.config import settings
from backend.models.schemas import SummarizeResponse, TermExplanation

logger = logging.getLogger("finnews.ai_service")

# In-memory cache for AI summaries to avoid duplicate LLM calls
AI_SUMMARY_CACHE: Dict[str, Dict[str, Any]] = {}
AI_CACHE_TTL_SECONDS = 1800  # 30 minutes

# Common financial terms lookup dictionary for intelligent fallback
FINANCIAL_GLOSSARY: Dict[str, str] = {
    "interest rate": "The cost of borrowing money set by central banks to control inflation and economic speed.",
    "inflation": "The rate at which the price of goods and services rises, eroding purchasing power.",
    "federal reserve": "The central bank of the United States that manages monetary policy and interest rates.",
    "fed": "The U.S. central bank responsible for keeping inflation stable and employment high.",
    "s&p 500": "An index tracking the stock performance of 500 of the largest publicly traded companies in the U.S.",
    "revenue": "The total amount of money a company brings in from sales before deducting expenses.",
    "gross margin": "The percentage of revenue a company retains after paying the direct costs of producing its goods.",
    "brent crude": "A major global trading benchmark for unrefined petroleum / crude oil.",
    "opec": "An organization of oil-producing countries that coordinates crude oil production levels.",
    "yield": "The income return on an investment (like a bond or stock), usually expressed as an annual percentage.",
    "cpi": "Consumer Price Index — a measure that tracks average changes in prices paid by consumers for goods and services.",
    "gpu": "Graphics Processing Unit — powerful chips widely used to run artificial intelligence algorithms.",
    "liquidity": "How quickly an asset can be converted into cash without affecting its market price.",
    "refinancing": "Replacing an existing debt obligation with a new loan under different interest rate terms.",
    "mortgage": "A loan specifically used to purchase real estate property."
}

def generate_fallback_summary(title: str, content: str, description: str = "") -> SummarizeResponse:
    """Intelligent rule-based financial simplifier when Groq API key is unconfigured or rate limited."""
    combined_text = f"{title}. {description}. {content}".strip()
    
    # 1. Simple Summary
    if description and len(description) > 30:
        clean_desc = description.split("...")[0].strip()
        summary = f"In simple terms: {clean_desc} This report highlights major updates in the market that impact general investors and businesses."
    else:
        summary = f"This report explains recent developments regarding '{title}'. It breaks down how recent announcements impact the market and everyday finances."

    # 2. Extract Key Points
    sentences = [part.strip() for part in combined_text.split(".") if len(part.strip()) > 15]
    key_points = []
    if len(sentences) >= 1:
        key_points.append(sentences[0] + ".")
    if len(sentences) >= 2:
        key_points.append(sentences[1] + ".")
    if len(sentences) >= 3:
        key_points.append(sentences[2] + ".")
    else:
        key_points.append(f"Focuses on key developments surrounding {title[:40]}.")
        key_points.append("Markets and analysts are closely tracking these economic indicators.")

    # 3. Why It Matters
    why_it_matters = (
        "This matter affects market sentiment, interest rates, or company valuations. "
        "Understanding these shifts helps individual investors make informed decisions about their savings and investments."
    )

    # 4. Financial Terms Extraction
    lower_text = combined_text.lower()
    terms: List[TermExplanation] = []
    for term, meaning in FINANCIAL_GLOSSARY.items():
        if term in lower_text:
            terms.append(TermExplanation(term=term.title(), meaning=meaning))
            if len(terms) >= 3:
                break
    
    if not terms:
        terms.append(TermExplanation(
            term="Market Volatility",
            meaning="The rate at which stock or commodity prices fluctuate over a short period."
        ))

    return SummarizeResponse(
        success=True,
        summary=summary,
        key_points=key_points[:3],
        why_it_matters=why_it_matters,
        terms=terms
    )

async def summarize_financial_article(title: str, content: str, description: str = "") -> SummarizeResponse:
    """
    Summarizes a financial article into simple terms using Groq LLM (llama-3.3-70b-versatile).
    Falls back gracefully if Groq API key is missing or request fails.
    Uses in-memory cache to prevent duplicate AI requests.
    """
    # Create deterministic hash key for article
    cache_key = hashlib.md5(f"{title}:{description[:100]}".encode("utf-8")).hexdigest()
    now = time.time()

    if cache_key in AI_SUMMARY_CACHE:
        entry = AI_SUMMARY_CACHE[cache_key]
        if now - entry["timestamp"] < AI_CACHE_TTL_SECONDS:
            logger.info(f"Serving AI summary from cache for: {title[:30]}")
            return entry["data"]

    api_key = settings.GROQ_API_KEY
    
    if not api_key or api_key == "your_groq_api_key_here":
        logger.info("Groq API key not provided. Using fallback AI summarizer.")
        return generate_fallback_summary(title, content, description)

    # Truncate content to avoid token limits
    truncated_content = content[:settings.MAX_CONTENT_CHARS] if content else description

    system_prompt = (
        "You are an expert financial journalist and educator who excels at translating complex "
        "financial news, corporate earnings, central bank decisions, and stock market terminology "
        "into clear, beginner-friendly explanations.\n\n"
        "RULES:\n"
        "1. Explain the news in simple, jargon-free plain English that a 15-year-old can easily understand.\n"
        "2. Never invent or hallucinate facts not present in the provided article text.\n"
        "3. Highlight specific numbers, percentages, or figures if available.\n"
        "4. Output MUST be strictly valid JSON matching this structure without additional text:\n"
        "{\n"
        '  "summary": "A 2-3 sentence clear summary in plain language.",\n'
        '  "key_points": ["First key takeaway", "Second key takeaway", "Third key takeaway"],\n'
        '  "why_it_matters": "1-2 sentences explaining real-world impact on everyday people or investors.",\n'
        '  "terms": [\n'
        '    {"term": "Financial Term 1", "meaning": "Simple 1-sentence definition"},\n'
        '    {"term": "Financial Term 2", "meaning": "Simple 1-sentence definition"}\n'
        "  ]\n"
        "}"
    )

    user_prompt = f"Headline: {title}\nSummary/Content: {truncated_content}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 800,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            
            if res.status_code != 200:
                logger.warning(f"Groq API returned status {res.status_code}: {res.text}. Utilizing fallback.")
                return generate_fallback_summary(title, content, description)

            res_data = res.json()
            raw_ai_text = res_data["choices"][0]["message"]["content"].strip()
            
            # Extract JSON if enclosed in markdown code fences
            if "```" in raw_ai_text:
                json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_ai_text, re.DOTALL)
                if json_match:
                    raw_ai_text = json_match.group(1)

            parsed = json.loads(raw_ai_text)
            
            terms_objs = []
            for t in parsed.get("terms", []):
                if isinstance(t, dict) and "term" in t and "meaning" in t:
                    terms_objs.append(TermExplanation(term=str(t["term"]), meaning=str(t["meaning"])))

            res_obj = SummarizeResponse(
                success=True,
                summary=parsed.get("summary", title),
                key_points=parsed.get("key_points", []),
                why_it_matters=parsed.get("why_it_matters", "Helps track financial markets."),
                terms=terms_objs
            )
            AI_SUMMARY_CACHE[cache_key] = {"timestamp": now, "data": res_obj}
            return res_obj

    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        fallback_res = generate_fallback_summary(title, content, description)
        AI_SUMMARY_CACHE[cache_key] = {"timestamp": now, "data": fallback_res}
        return fallback_res
