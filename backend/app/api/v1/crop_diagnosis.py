from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from app.services.diagnosis_service import diagnosis_service

router = APIRouter()


@router.post("/diagnose")
async def diagnose_crop_disease(
    image: UploadFile = File(...), description: str | None = Form(None)
) -> dict[str, Any]:
    """
    Diagnose crop disease from uploaded image using FormData

    TODO: Implement the following:
    1. ✅ Validate image format (JPEG, PNG)
    2. Upload image to Google Cloud Storage
    3. Call Gemini 2.0 Flash for disease identification
    4. Process AI response and extract disease info
    5. Return structured diagnosis with treatment recommendations
    """
    return await diagnosis_service.diagnose_crop_from_upload(image, description)


@router.get("/diseases")
async def get_common_diseases():
    """
    Get list of common crop diseases

    TODO: Implement database/cache of common diseases
    """
    return diagnosis_service.get_common_diseases()


# TODO: Add endpoint for disease prevention tips
# TODO: Add endpoint for treatment tracking
# TODO: Add endpoint for uploading multiple images
