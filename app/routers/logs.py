# app/routers/logs.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.core import scanner

router = APIRouter()

# Fetch recent logs
@router.get("/recent")
async def get_recent_logs(limit: int = Query(50, description="Number of recent logs to fetch")):
    try:
        return scanner.recent_logs(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search logs with query
@router.get("/search")
async def search_logs(
    query: str = Query(..., description="Search query string"),
    start_time: Optional[str] = Query(None, description="Start timestamp (ISO format)"),
    end_time: Optional[str] = Query(None, description="End timestamp (ISO format)")
):
    try:
        results = scanner.search_logs(query=query, start=start_time, end=end_time)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
