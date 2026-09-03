from typing import Any, Dict, List

from pydantic import BaseModel


class DashboardGenerationRequest(BaseModel):
    dataset_id: str
    prompt: str


class DashboardGenerationResponse(BaseModel):
    dataset_id: str
    prompt: str
    dashboard_title: str
    status: str
    pages: List[Dict[str, Any]]