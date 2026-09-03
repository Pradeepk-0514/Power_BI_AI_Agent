from typing import List
from pydantic import BaseModel


class PowerBIProjectRequest(BaseModel):
    dataset_id: str
    prompt: str


class PowerBIProjectFile(BaseModel):
    path: str
    content: str


class PowerBIProjectResponse(BaseModel):
    dataset_id: str
    prompt: str
    project_name: str
    status: str
    project_type: str
    files: List[PowerBIProjectFile]