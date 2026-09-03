from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.dataset_service import dataset_service
from app.agents.dataset_agent import DatasetUnderstandingAgent

dataset_agent = DatasetUnderstandingAgent()

router = APIRouter(
    prefix="/api",
    tags=["Dataset"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are supported"
        )

    file_path = UPLOAD_DIR / file.filename

    try:
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(exc)}"
        )

    dataset = dataset_service.register_dataset(
        filename=file.filename,
        file_path=str(file_path)
    )

    return {
        "status": "success",
        "dataset_id": dataset["dataset_id"],
        "filename": dataset["filename"],
        "file_path": dataset["file_path"],
        "dataset_status": dataset["status"]
    }

@router.post("/dataset/{dataset_id}/analyze")
def analyze_dataset(dataset_id: str):

    dataset = dataset_service.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        profile = dataset_agent.analyze(
            dataset["file_path"]
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset analysis failed: {str(exc)}"
        )

    updated_dataset = dataset_service.update_profile(
        dataset_id,
        profile
    )

    return updated_dataset

@router.get("/dataset/{dataset_id}")
def get_dataset(dataset_id: str):

    dataset = dataset_service.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return dataset