# app/routers/dashboard.py

from fastapi import APIRouter, HTTPException
from app.core import scanner

router = APIRouter()

# Overview for dashboard
@router.get("/overview")
async def dashboard_overview():
    """
    Returns a quick summary of the system status for the dashboard.
    """
    try:
        return scanner.dashboard_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trends for dashboard
@router.get("/trends")
async def dashboard_trends():
    """
    Returns minimal trend data (can be expanded later for charts).
    """
    try:
        return scanner.dashboard_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
