"""
Pydantic models for Crop Diagnosis API with GCS Image URLs
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Complex models matching the agent prompt structure
class CropIdentification(BaseModel):
    """Crop identification details"""

    crop_name: Optional[str] = Field(None, description="Specific crop name")
    variety_hints: Optional[str] = Field(
        None, description="Any variety clues from visual characteristics"
    )
    growth_stage: Optional[str] = Field(
        None, description="Growth stage: seedling|vegetative|flowering|fruiting|mature"
    )
    confidence_percentage: Optional[int] = Field(
        None, description="Confidence percentage for crop identification"
    )


class PrimaryDiagnosis(BaseModel):
    """Primary disease diagnosis details"""

    disease_name: Optional[str] = Field(None, description="Specific disease name")
    scientific_name: Optional[str] = Field(None, description="Pathogen scientific name if known")
    confidence_percentage: Optional[int] = Field(
        None, description="Confidence percentage for diagnosis"
    )
    severity_level: Optional[str] = Field(
        None, description="Severity: mild|moderate|severe|critical"
    )
    affected_area_percentage: Optional[int] = Field(None, description="Percentage of affected area")


class DiseaseAnalysis(BaseModel):
    """Disease analysis details"""

    disease_detected: Optional[bool] = Field(None, description="Whether disease was detected")
    primary_diagnosis: Optional[PrimaryDiagnosis] = Field(
        None, description="Primary diagnosis details"
    )
    differential_diagnosis: Optional[List[str]] = Field(
        None, description="Alternative diagnoses to consider"
    )
    symptoms_observed: Optional[List[str]] = Field(None, description="List of observed symptoms")


class ImmediateAction(BaseModel):
    """Immediate action recommendations"""

    steps: Optional[List[str]] = Field(None, description="Immediate steps to take")
    urgency: Optional[str] = Field(None, description="Urgency level: high|medium|low")


class OrganicTreatment(BaseModel):
    """Organic treatment recommendations"""

    primary_recommendation: Optional[str] = Field(None, description="Primary organic treatment")
    application_method: Optional[str] = Field(None, description="How to apply the treatment")
    frequency: Optional[str] = Field(None, description="Application frequency")
    local_availability: Optional[str] = Field(None, description="Local availability information")


class ChemicalTreatment(BaseModel):
    """Chemical treatment recommendations"""

    primary_recommendation: Optional[str] = Field(None, description="Primary chemical treatment")
    dosage: Optional[str] = Field(None, description="Dosage information")
    application_method: Optional[str] = Field(None, description="How to apply the treatment")
    frequency: Optional[str] = Field(None, description="Application frequency")
    precautions: Optional[str] = Field(None, description="Safety precautions")
    indian_brands: Optional[List[str]] = Field(None, description="Available Indian brands")


class CostAnalysis(BaseModel):
    """Cost analysis for treatments"""

    organic_cost_per_acre: Optional[str] = Field(
        None, description="Organic treatment cost per acre"
    )
    chemical_cost_per_acre: Optional[str] = Field(
        None, description="Chemical treatment cost per acre"
    )
    recommendation: Optional[str] = Field(
        None, description="Recommended approach: organic|chemical|integrated"
    )


class TreatmentRecommendations(BaseModel):
    """Treatment recommendations"""

    immediate_action: Optional[ImmediateAction] = Field(
        None, description="Immediate actions to take"
    )
    organic_treatment: Optional[OrganicTreatment] = Field(
        None, description="Organic treatment options"
    )
    chemical_treatment: Optional[ChemicalTreatment] = Field(
        None, description="Chemical treatment options"
    )
    cost_analysis: Optional[CostAnalysis] = Field(None, description="Cost analysis for treatments")


class PreventionMeasures(BaseModel):
    """Prevention measures"""

    cultural_practices: Optional[List[str]] = Field(
        None, description="Cultural practices for prevention"
    )
    resistant_varieties: Optional[List[str]] = Field(
        None, description="Resistant varieties recommended"
    )
    seasonal_timing: Optional[str] = Field(None, description="Best timing for planting/treatment")


class FollowUp(BaseModel):
    """Follow-up instructions"""

    monitoring_schedule: Optional[str] = Field(None, description="When to check again")
    success_indicators: Optional[List[str]] = Field(
        None, description="Signs of successful treatment"
    )
    escalation_triggers: Optional[List[str]] = Field(None, description="When to seek further help")
    lab_testing_needed: Optional[bool] = Field(
        None, description="Whether lab testing is recommended"
    )


# Simple models for backward compatibility
class CropHealthDiagnosis(BaseModel):
    """Simplified crop health diagnosis data"""
    crop_detected: Optional[str] = Field(None, description="Type of crop detected")
    disease_detected: Optional[bool] = Field(None, description="Whether disease was detected")
    disease_name: Optional[str] = Field(None, description="Name of the detected disease")
    confidence: Optional[str] = Field(None, description="Confidence level of diagnosis")
    severity: Optional[str] = Field(None, description="Severity level of the disease")
    description: Optional[str] = Field(None, description="Detailed description of the diagnosis")


class TreatmentRecommendation(BaseModel):
    """Simplified treatment recommendations"""
    organic_treatment: Optional[str] = Field(None, description="Organic treatment options")
    chemical_treatment: Optional[str] = Field(None, description="Chemical treatment options")
    application_frequency: Optional[str] = Field(None, description="How often to apply treatments")
    immediate_action: Optional[str] = Field(None, description="Immediate actions to take")


class PreventionNotes(BaseModel):
    """Simplified prevention and additional notes"""
    preventive_measures: Optional[str] = Field(None, description="Preventive measures for future")
    differential_diagnosis: Optional[str] = Field(
        None, description="Alternative diagnoses to consider"
    )


class CropDiagnosisImageRequest(BaseModel):
    """Request model for crop diagnosis using GCS image URL"""

    image_url: str = Field(
        ..., description="Google Cloud Storage URL of the crop image", min_length=1
    )
    description: Optional[str] = Field(
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
    description: Optional[str] = Field(None, description="Description provided with the image")
    uploaded_filename: Optional[str] = Field(
        None, description="Original filename if image was uploaded"
    )

    # Complex structured diagnosis data (matching agent prompt)
    crop_identification: Optional[CropIdentification] = Field(
        None, description="Crop identification details"
    )
    disease_analysis: Optional[DiseaseAnalysis] = Field(
        None, description="Disease analysis details"
    )
    treatment_recommendations: Optional[TreatmentRecommendations] = Field(
        None, description="Treatment recommendations"
    )
    prevention_measures: Optional[PreventionMeasures] = Field(
        None, description="Prevention measures"
    )
    follow_up: Optional[FollowUp] = Field(None, description="Follow-up instructions")

    # Simple structured diagnosis data (for backward compatibility)
    crop_health_diagnosis: Optional[CropHealthDiagnosis] = Field(
        None, description="Simplified crop health diagnosis"
    )
    treatment_recommendation: Optional[TreatmentRecommendation] = Field(
        None, description="Simplified treatment recommendations"
    )
    prevention_notes: Optional[PreventionNotes] = Field(
        None, description="Simplified prevention notes"
    )

    disclaimer: Optional[str] = Field(None, description="Disclaimer about AI diagnosis")

    # Raw response for debugging/fallback
    raw_agent_response: Optional[str] = Field(
        None, description="Raw response from crop diagnosis agent"
    )

    error: Optional[str] = Field(None, description="Error message if request failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "image_url": "gs://kisan-ai-bucket/crop_diagnosis/uploaded_image_123.jpg",
                "description": "My tomato plants have brown spots on leaves",
                "uploaded_filename": "tomato_disease.jpg",
                "crop_identification": {
                    "crop_name": "tomato",
                    "growth_stage": "vegetative",
                    "confidence_percentage": 95,
                },
                "disease_analysis": {
                    "disease_detected": True,
                    "primary_diagnosis": {
                        "disease_name": "Early Blight",
                        "confidence_percentage": 85,
                        "severity_level": "moderate",
                    },
                },
                "disclaimer": "AI diagnosis for reference only. Consult local agricultural experts.",
                "error": None,
            }
        }
