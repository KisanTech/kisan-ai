"""
Pydantic models for Crop Diagnosis API with GCS Image URLs
"""

from pydantic import BaseModel, Field


class CropHealthDiagnosis(BaseModel):
    """Structured crop health diagnosis data"""

    crop_detected: str | None = Field(None, description="Type of crop detected")
    disease_detected: bool | None = Field(None, description="Whether disease was detected")
    disease_name: str | None = Field(None, description="Name of the detected disease")
    confidence: str | None = Field(None, description="Confidence level of diagnosis")
    severity: str | None = Field(None, description="Severity level of the disease")
    description: str | None = Field(None, description="Detailed description of the diagnosis")


class TreatmentRecommendation(BaseModel):
    """Structured treatment recommendations"""

    organic_treatment: str | None = Field(None, description="Organic treatment options")
    chemical_treatment: str | None = Field(None, description="Chemical treatment options")
    application_frequency: str | None = Field(None, description="How often to apply treatments")
    immediate_action: str | None = Field(None, description="Immediate actions to take")


class PreventionNotes(BaseModel):
    """Prevention and additional notes"""

    preventive_measures: str | None = Field(None, description="Preventive measures for future")
    differential_diagnosis: str | None = Field(
        None, description="Alternative diagnoses to consider"
    )


class CropDiagnosisImageRequest(BaseModel):
    """Request model for crop diagnosis using GCS image URL"""

    image_url: str = Field(
        ..., description="Google Cloud Storage URL of the crop image", min_length=1
    )
    description: str | None = Field(
        None, description="Optional description of the crop/issue", max_length=1000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "gs://kisan-ai-bucket/crops/tomato_disease_sample.jpg",
                "description": "My tomato plants have brown spots on leaves",
            }
        }


class CropDiagnosisImageResponse(BaseModel):
    """Response model for crop diagnosis using GCS image URL or uploaded file"""

    success: bool = Field(..., description="Whether the request was successful")
    image_url: str = Field(..., description="GCS URL of the analyzed image")
    description: str | None = Field(None, description="Description provided with the image")
    uploaded_filename: str | None = Field(
        None, description="Original filename if image was uploaded"
    )

    # Structured diagnosis data
    crop_health_diagnosis: CropHealthDiagnosis | None = Field(
        None, description="Structured crop health diagnosis"
    )
    treatment_recommendation: TreatmentRecommendation | None = Field(
        None, description="Structured treatment recommendations"
    )
    prevention_notes: PreventionNotes | None = Field(
        None, description="Prevention notes and additional information"
    )
    disclaimer: str | None = Field(None, description="Disclaimer about AI diagnosis")

    # Raw response for debugging/fallback
    raw_agent_response: str | None = Field(
        None, description="Raw response from crop diagnosis agent"
    )

    error: str | None = Field(None, description="Error message if request failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "image_url": "gs://kisan-ai-bucket/crop_diagnosis/uploaded_image_123.jpg",
                "description": "My tomato plants have brown spots on leaves",
                "uploaded_filename": "tomato_disease.jpg",
                "crop_health_diagnosis": {
                    "crop_detected": "tomato",
                    "disease_detected": True,
                    "disease_name": "Early Blight",
                    "confidence": "85%",
                    "severity": "Moderate",
                    "description": "The leaves show characteristic brown spots with concentric rings",
                },
                "treatment_recommendation": {
                    "organic_treatment": "Apply neem oil spray",
                    "chemical_treatment": "Use copper-based fungicide",
                    "application_frequency": "Every 7 days for 3 weeks",
                    "immediate_action": "Remove affected leaves",
                },
                "prevention_notes": {
                    "preventive_measures": "Ensure proper spacing and air circulation",
                    "differential_diagnosis": "Consider bacterial spot if symptoms worsen",
                },
                "disclaimer": "AI diagnosis for reference only. Consult local agricultural experts.",
                "error": None,
            }
        }
