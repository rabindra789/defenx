# app/routers/incidents.py

from fastapi import APIRouter, HTTPException
from app.core import scanner

router = APIRouter()

# List all incidents
@router.get("/all")
async def list_all_incidents():
    try:
        return scanner.list_incidents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get specific incident
@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    try:
        incident = scanner.get_incident(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        return incident
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
