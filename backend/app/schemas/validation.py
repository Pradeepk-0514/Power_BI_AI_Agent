from pydantic import BaseModel
from typing import List


class ValidationRequest(BaseModel):
    dataset_id: str
    prompt: str


class ValidationIssue(BaseModel):
    step: int
    field: str
    value: str
    message: str


class ValidationResponse(BaseModel):
    dataset_id: str
    prompt: str
    valid: bool
    issues: List[ValidationIssue]