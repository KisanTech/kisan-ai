from typing import Any

from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/diagnose")
async def diagnose_crop_disease(
    image: UploadFile = File(...), description: str = None
) -> dict[str, Any]:
    """
    Diagnose crop disease from uploaded image

    TODO: Implement the following:
    1. Validate image format (JPEG, PNG)
    2. Upload image to Google Cloud Storage
    3. Call Gemini 2.0 Flash for disease identification
    4. Process AI response and extract disease info
    5. Return structured diagnosis with treatment recommendations
    """

    # Placeholder response for demo
    return {
        "diagnosis": {
            "disease_name": "Early Blight",
            "confidence": 0.95,
            "severity": "moderate",
            "affected_area": "leaves",
        },
        "treatment": {
            "immediate_action": "Remove affected leaves",
            "recommended_fungicide": "Copper-based fungicide",
            "application_frequency": "Every 7 days for 3 weeks",
        },
        "local_suppliers": [{"name": "Agricultural Store Bangalore", "distance": "2.5 km"}],
    }


@router.get("/diseases")
async def get_common_diseases():
    """
    Get list of common crop diseases

    TODO: Implement database/cache of common diseases
    """
    return {"diseases": ["Early Blight", "Late Blight", "Bacterial Wilt", "Powdery Mildew"]}


# TODO: Add endpoint for disease prevention tips
# TODO: Add endpoint for treatment tracking
# TODO: Add endpoint for uploading multiple images
