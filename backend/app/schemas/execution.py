from typing import Any

from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    dataset_id: str
    prompt: str


class ExecutionResponse(BaseModel):
    dataset_id: str
    prompt: str
    intent: str
    results: list[dict[str, Any]]