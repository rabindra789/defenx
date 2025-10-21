# app/routers/phishing.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.phishing import PhishingScanner

router = APIRouter()
scanner = PhishingScanner()  # Use default keywords/domains; can be customized

# Request model
class EmailScanRequest(BaseModel):
    content: str
    custom_keywords: Optional[List[str]] = None
    custom_domains: Optional[List[str]] = None

# Response model
class EmailScanResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: List[str]

@router.post("/scan", response_model=EmailScanResponse)
async def scan_email_endpoint(request: EmailScanRequest):
    try:
        # If user provides custom keywords/domains, override defaults
        if request.custom_keywords or request.custom_domains:
            temp_scanner = PhishingScanner(
                keywords=request.custom_keywords,
                domains=request.custom_domains
            )
        else:
            temp_scanner = scanner

        result = temp_scanner.scan_email(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
