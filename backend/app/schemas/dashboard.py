from typing import List, Optional
from pydantic import BaseModel


# =========================================================
# Module 5.1 — Dashboard Planning
# =========================================================

class DashboardPlanRequest(BaseModel):
    dataset_id: str
    prompt: str


class DashboardVisual(BaseModel):
    title: str
    visual_type: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None


class DashboardPage(BaseModel):
    page_number: int
    page_name: str
    purpose: str
    visuals: List[DashboardVisual] = []


class DashboardPlanResponse(BaseModel):
    dataset_id: str
    prompt: str
    dashboard_title: str
    description: str
    pages: List[DashboardPage]


# =========================================================
# Compatibility names
# =========================================================

# If your existing dashboard.py API imports DashboardRequest,
# keep this alias so it does not break.
DashboardRequest = DashboardPlanRequest


# =========================================================
# Module 5.2 — Dashboard Layout
# =========================================================

class DashboardLayoutRequest(BaseModel):
    dataset_id: str
    prompt: str


class LayoutVisual(BaseModel):
    title: str
    visual_type: str

    x_axis: Optional[dict] = None
    y_axis: Optional[dict] = None

    position: Optional[dict] = None

    width: Optional[int] = None
    height: Optional[int] = None


class DashboardLayoutPage(BaseModel):
    page_number: int
    page_name: str
    layout_type: str
    visuals: List[LayoutVisual]


class DashboardLayoutResponse(BaseModel):
    dataset_id: str
    prompt: str
    dashboard_title: str
    pages: List[DashboardLayoutPage]