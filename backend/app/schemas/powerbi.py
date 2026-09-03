from typing import Any, Dict, List

from pydantic import BaseModel, Field


# =========================================================
# REQUEST
# =========================================================

class PowerBIProjectRequest(BaseModel):
    dataset_id: str
    prompt: str


# =========================================================
# FILE INFORMATION
# =========================================================

class PowerBIFile(BaseModel):
    path: str
    content: str


# =========================================================
# RESPONSE
# =========================================================

class PowerBIProjectResponse(BaseModel):
    dataset_id: str
    prompt: str
    project_name: str
    status: str
    project_type: str
    files: List[PowerBIFile]