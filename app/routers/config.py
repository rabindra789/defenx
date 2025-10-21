# app/routers/config.py

from fastapi import APIRouter, HTTPException
from app.core import scanner

router = APIRouter()

# Get current config
@router.get("/")
async def get_config():
    try:
        return scanner.CONFIG
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update configuration
@router.post("/update")
async def update_config(config_data: dict):
    try:
        scanner.CONFIG.update(config_data)
        return {"message": "Configuration updated", "config": scanner.CONFIG}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
