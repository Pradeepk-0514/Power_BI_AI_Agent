from typing import List, Optional
from pydantic import BaseModel


class DashboardLayoutRequest(BaseModel):
    dataset_id: str
    prompt: str


class Position(BaseModel):
    x: int
    y: int
    width: int
    height: int


class DashboardVisual(BaseModel):
    visual_id: str
    visual_type: str
    title: str
    position: Position
    configuration: Optional[dict] = None


class DashboardLayoutResponse(BaseModel):
    dataset_id: str
    prompt: str
    dashboard_title: str
    pages: List[dict]