"""
Crop Diagnosis API endpoints for GCS Image URLs and File Uploads.

This module provides REST API endpoints for crop diagnosis using
Google Cloud Storage image URLs or file uploads with AI agent processing.
"""

import datetime
import json
import uuid

from app.agents.crop_diagnosis_agent.agent import root_agent
from app.models.crop_diagnosis import (
    ChemicalTreatment,
    CostAnalysis,
    CropDiagnosisImageRequest,
    CropDiagnosisImageResponse,
    CropHealthDiagnosis,
    CropIdentification,
    DiseaseAnalysis,
    FollowUp,
    ImmediateAction,
    OrganicTreatment,
    PreventionMeasures,
    PreventionNotes,
    PrimaryDiagnosis,
    TreatmentRecommendation,
    TreatmentRecommendations,
)
from app.utils.gcp.gcp_manager import gcp_manager
from app.utils.logger import logger
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

router = APIRouter(tags=["crop-diagnosis"])

# Constants
APP_NAME = "kisan_ai_crop_diagnosis"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def setup_session_and_runner():
    """Setup session and runner for crop diagnosis agent interaction"""
    # Generate simple IDs for the session
    user_id = f"crop_user_{uuid.uuid4().hex[:8]}"
    session_id = f"crop_session_{uuid.uuid4().hex[:8]}"

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner, user_id, session_id


def parse_agent_json_response(response_text: str) -> tuple:
    """
    Parse JSON response from crop diagnosis agent

    Returns:
        Tuple of complex structured data models or None values if parsing fails
    """
    try:
        # Try to parse the response as JSON
        structured_data = json.loads(response_text)

        # Extract crop identification
        crop_identification = None
        if "crop_identification" in structured_data:
            ci_data = structured_data["crop_identification"]
            crop_identification = CropIdentification(
                crop_name=ci_data.get("crop_name"),
                variety_hints=ci_data.get("variety_hints"),
                growth_stage=ci_data.get("growth_stage"),
                confidence_percentage=ci_data.get("confidence_percentage"),
            )

        # Extract disease analysis
        disease_analysis = None
        if "disease_analysis" in structured_data:
            da_data = structured_data["disease_analysis"]

            # Extract primary diagnosis
            primary_diagnosis = None
            if "primary_diagnosis" in da_data:
                pd_data = da_data["primary_diagnosis"]
                primary_diagnosis = PrimaryDiagnosis(
                    disease_name=pd_data.get("disease_name"),
                    scientific_name=pd_data.get("scientific_name"),
                    confidence_percentage=pd_data.get("confidence_percentage"),
                    severity_level=pd_data.get("severity_level"),
                    affected_area_percentage=pd_data.get("affected_area_percentage"),
                )

            disease_analysis = DiseaseAnalysis(
                disease_detected=da_data.get("disease_detected"),
                primary_diagnosis=primary_diagnosis,
                differential_diagnosis=da_data.get("differential_diagnosis"),
                symptoms_observed=da_data.get("symptoms_observed"),
            )

        # Extract treatment recommendations
        treatment_recommendations = None
        if "treatment_recommendations" in structured_data:
            tr_data = structured_data["treatment_recommendations"]

            # Extract immediate action
            immediate_action = None
            if "immediate_action" in tr_data:
                ia_data = tr_data["immediate_action"]
                immediate_action = ImmediateAction(
                    steps=ia_data.get("steps"), urgency=ia_data.get("urgency")
                )

            # Extract organic treatment
            organic_treatment = None
            if "organic_treatment" in tr_data:
                ot_data = tr_data["organic_treatment"]
                organic_treatment = OrganicTreatment(
                    primary_recommendation=ot_data.get("primary_recommendation"),
                    application_method=ot_data.get("application_method"),
                    frequency=ot_data.get("frequency"),
                    local_availability=ot_data.get("local_availability"),
                )

            # Extract chemical treatment
            chemical_treatment = None
            if "chemical_treatment" in tr_data:
                ct_data = tr_data["chemical_treatment"]
                chemical_treatment = ChemicalTreatment(
                    primary_recommendation=ct_data.get("primary_recommendation"),
                    dosage=ct_data.get("dosage"),
                    application_method=ct_data.get("application_method"),
                    frequency=ct_data.get("frequency"),
                    precautions=ct_data.get("precautions"),
                    indian_brands=ct_data.get("indian_brands"),
                )

            # Extract cost analysis
            cost_analysis = None
            if "cost_analysis" in tr_data:
                ca_data = tr_data["cost_analysis"]
                cost_analysis = CostAnalysis(
                    organic_cost_per_acre=ca_data.get("organic_cost_per_acre"),
                    chemical_cost_per_acre=ca_data.get("chemical_cost_per_acre"),
                    recommendation=ca_data.get("recommendation"),
                )

            treatment_recommendations = TreatmentRecommendations(
                immediate_action=immediate_action,
                organic_treatment=organic_treatment,
                chemical_treatment=chemical_treatment,
                cost_analysis=cost_analysis,
            )

        # Extract prevention measures
        prevention_measures = None
        if "prevention_measures" in structured_data:
            pm_data = structured_data["prevention_measures"]
            prevention_measures = PreventionMeasures(
                cultural_practices=pm_data.get("cultural_practices"),
                resistant_varieties=pm_data.get("resistant_varieties"),
                seasonal_timing=pm_data.get("seasonal_timing"),
            )

        # Extract follow up
        follow_up = None
        if "follow_up" in structured_data:
            fu_data = structured_data["follow_up"]
            follow_up = FollowUp(
                monitoring_schedule=fu_data.get("monitoring_schedule"),
                success_indicators=fu_data.get("success_indicators"),
                escalation_triggers=fu_data.get("escalation_triggers"),
                lab_testing_needed=fu_data.get("lab_testing_needed"),
            )

        # Extract disclaimer
        disclaimer = structured_data.get("disclaimer")

        return (
            crop_identification,
            disease_analysis,
            treatment_recommendations,
            prevention_measures,
            follow_up,
            disclaimer,
        )

    except json.JSONDecodeError as e:
        logger.warning(
            "Failed to parse agent response as JSON",
            error=str(e),
            response_preview=response_text[:200] if response_text else "empty",
        )
        return None, None, None, None, None, None


async def upload_image_to_gcs(image: UploadFile) -> str:
    """
    Upload image to Google Cloud Storage and return the GCS URL

    Args:
        image: Uploaded image file

    Returns:
        GCS URL of the uploaded image

    Raises:
        HTTPException: If upload fails
    """
    try:
        # Validate file type
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        # Read image data
        image_data = await image.read()

        # Validate file size
        if len(image_data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = image.filename.split(".")[-1] if "." in image.filename else "jpg"
        unique_filename = f"crop_diagnosis/{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"

        # Upload to GCS
        storage_client = gcp_manager.storage
        blob = storage_client.upload_blob(
            source_data=image_data,
            destination_blob_name=unique_filename,
            content_type=image.content_type,
        )

        # Generate URLs using the blob object
        gcs_url = f"gs://{storage_client._bucket_name}/{unique_filename}"

        # Try to get the public URL from the blob
        try:
            # Ensure the blob is public
            blob.make_public()
            public_url = blob.public_url
        except Exception as e:
            logger.warning(f"Failed to make blob public: {e}, using direct URL")
            public_url = (
                f"https://storage.googleapis.com/{storage_client._bucket_name}/{unique_filename}"
            )

        logger.info(
            "Image uploaded to GCS successfully",
            original_filename=image.filename,
            gcs_url=gcs_url,
            public_url=public_url,
            file_size_kb=len(image_data) / 1024,
        )

        return public_url

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to upload image to GCS",
            error=str(e),
            error_type=type(e).__name__,
            filename=getattr(image, "filename", "unknown"),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )


async def call_crop_diagnosis_agent(image_url: str, description: str) -> str:
    """Call the crop diagnosis agent with image URL and description"""
    try:
        # Prepare the query parts
        query_parts = ["Please analyze this crop image for disease diagnosis."]
        if description:
            query_parts.append(f"Additional context: {description}")

        query = "\n".join(query_parts)

        # Create content with both text and image URL as separate parts
        content = types.Content(
            role="user",
            parts=[
                types.Part(text=query),
                types.Part(file_data=types.FileData(file_uri=image_url, mime_type="image/jpeg")),
            ],
        )
        session, runner, user_id, session_id = await setup_session_and_runner()
        events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                logger.info(
                    "Crop diagnosis agent response received",
                    response_length=len(final_response),
                    image_url=image_url,
                )
                return final_response

        # If no final response found
        return "I apologize, but I couldn't analyze the crop image at the moment. Please try again."

    except Exception as e:
        logger.error(
            "Crop diagnosis agent call failed",
            error=str(e),
            error_type=type(e).__name__,
            image_url=image_url,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop diagnosis processing failed: {str(e)}",
        )


@router.post(
    "/analyze-image",
    response_model=CropDiagnosisImageResponse,
    summary="Analyze crop image from GCS URL using AI agent",
    description="Analyze crop disease/health from Google Cloud Storage image URL using "
    "specialized crop diagnosis AI agent",
)
async def analyze_crop_image(request: CropDiagnosisImageRequest) -> CropDiagnosisImageResponse:
    """
    Analyze crop image from GCS URL using AI agent

    Args:
        request: Crop diagnosis request containing GCS image URL and optional description

    Returns:
        CropDiagnosisImageResponse containing structured analysis results

    Raises:
        HTTPException: If image URL validation or agent processing fails
    """
    try:
        logger.info(
            "Crop diagnosis image request received",
            image_url=request.image_url,
            description_length=len(request.description) if request.description else 0,
        )

        # Validate image URL
        if not request.image_url.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Image URL cannot be empty"
            )

        # Basic validation for GCS URLs
        if not (
            request.image_url.startswith("gs://")
            or request.image_url.startswith("https://storage.googleapis.com/")
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image URL must be a valid Google Cloud Storage URL (gs:// or https://storage.googleapis.com/)",
            )

        # Convert GCS URL to public HTTP URL if needed
        image_url_for_agent = request.image_url
        if request.image_url.startswith("gs://"):
            # Convert gs://bucket/path to https://storage.googleapis.com/bucket/path
            bucket_and_path = request.image_url.replace("gs://", "")
            image_url_for_agent = f"https://storage.googleapis.com/{bucket_and_path}"

        # Call crop diagnosis agent
        agent_response = await call_crop_diagnosis_agent(
            image_url=image_url_for_agent, description=request.description or ""
        )

        logger.info(
            "Crop diagnosis agent processing completed", agent_response_length=len(agent_response)
        )

        # Parse structured JSON response from agent
        (
            crop_identification,
            disease_analysis,
            treatment_recommendations,
            prevention_measures,
            follow_up,
            disclaimer,
        ) = parse_agent_json_response(agent_response)

        # Return the complete response
        return CropDiagnosisImageResponse(
            success=True,
            image_url=request.image_url,
            description=request.description,
            crop_identification=crop_identification,
            disease_analysis=disease_analysis,
            treatment_recommendations=treatment_recommendations,
            prevention_measures=prevention_measures,
            follow_up=follow_up,
            disclaimer=disclaimer,
            raw_agent_response=agent_response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in crop diagnosis image analysis",
            error=str(e),
            error_type=type(e).__name__,
            image_url=getattr(request, "image_url", "unknown"),
        )
        # Return error response instead of raising exception
        return CropDiagnosisImageResponse(
            success=False,
            image_url=getattr(request, "image_url", "unknown"),
            error=f"Internal server error during crop diagnosis: {str(e)}",
        )


@router.post(
    "/analyze-upload",
    response_model=CropDiagnosisImageResponse,
    summary="Upload and analyze crop image using AI agent",
    description="Upload crop image, store in GCS, and analyze using specialized "
    "crop diagnosis AI agent",
)
async def analyze_uploaded_image(
    image: UploadFile = File(..., description="Crop image file to analyze"),
    description: str | None = Form(None, description="Optional description of the crop/issue"),
) -> CropDiagnosisImageResponse:
    """
    Upload and analyze crop image using AI agent

    Args:
        image: Uploaded crop image file
        description: Optional description of the crop/issue

    Returns:
        CropDiagnosisImageResponse containing structured analysis results

    Raises:
        HTTPException: If file upload, validation, or agent processing fails
    """
    try:
        logger.info(
            "Crop diagnosis upload request received",
            filename=image.filename,
            content_type=image.content_type,
            description_length=len(description) if description else 0,
        )

        # Upload image to GCS
        gcs_url = await upload_image_to_gcs(image)

        # Call crop diagnosis agent with the uploaded image URL
        agent_response = await call_crop_diagnosis_agent(
            image_url=gcs_url, description=description or ""
        )

        logger.info(
            "Crop diagnosis agent processing completed",
            agent_response_length=len(agent_response),
            uploaded_filename=image.filename,
        )

        # Parse structured JSON response from agent
        (
            crop_identification,
            disease_analysis,
            treatment_recommendations,
            prevention_measures,
            follow_up,
            disclaimer,
        ) = parse_agent_json_response(agent_response)

        # Return the complete response
        return CropDiagnosisImageResponse(
            success=True,
            image_url=gcs_url,
            description=description,
            uploaded_filename=image.filename,
            crop_identification=crop_identification,
            disease_analysis=disease_analysis,
            treatment_recommendations=treatment_recommendations,
            prevention_measures=prevention_measures,
            follow_up=follow_up,
            disclaimer=disclaimer,
            raw_agent_response=agent_response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in crop diagnosis upload analysis",
            error=str(e),
            error_type=type(e).__name__,
            filename=getattr(image, "filename", "unknown"),
        )
        # Return error response instead of raising exception
        return CropDiagnosisImageResponse(
            success=False,
            image_url="",
            uploaded_filename=getattr(image, "filename", "unknown"),
            error=f"Internal server error during crop diagnosis: {str(e)}",
        )
