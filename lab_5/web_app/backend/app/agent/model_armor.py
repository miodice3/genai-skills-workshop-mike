"""Model Armor integration for prompt and response safety validation."""

from google.cloud import modelarmor_v1
from google.api_core.client_options import ClientOptions
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global client instance (lazy initialized)
_model_armor_client: Optional[modelarmor_v1.ModelArmorClient] = None


def get_model_armor_client(model_armor_location: str) -> modelarmor_v1.ModelArmorClient:
    """
    Get or create Model Armor client instance.

    Args:
        model_armor_location: Model Armor service location (e.g., "us")

    Returns:
        ModelArmorClient instance
    """
    global _model_armor_client

    if _model_armor_client is None:
        model_armor_endpoint = f"modelarmor.{model_armor_location}.rep.googleapis.com"
        _model_armor_client = modelarmor_v1.ModelArmorClient(
            client_options=ClientOptions(api_endpoint=model_armor_endpoint)
        )
        logger.info(f"Model Armor client initialized with endpoint: {model_armor_endpoint}")

    return _model_armor_client


def check_prompt_with_model_armor(
    prompt: str, project_id: str, model_armor_location: str, template_id: str
) -> bool:
    """
    Check user prompt against Model Armor template.

    Args:
        prompt: The user's input string
        project_id: GCP project ID
        model_armor_location: Model Armor service location (e.g., "us")
        template_id: Model Armor template ID for prompt validation

    Returns:
        True if the prompt is safe to proceed, False if it should be blocked
    """
    logger.info(f"Checking prompt with Model Armor template: {template_id}")

    client = get_model_armor_client(model_armor_location)

    # Construct the resource name for the template
    template_name = client.template_path(project_id, model_armor_location, template_id)

    # Prepare the prompt data object
    user_prompt_data = modelarmor_v1.DataItem(text=prompt)

    # Create the request
    ma_request = modelarmor_v1.SanitizeUserPromptRequest(
        name=template_name,
        user_prompt_data=user_prompt_data,
    )

    # Call the Model Armor service
    ma_response = client.sanitize_user_prompt(request=ma_request)

    # Check the result. MATCH_FOUND means a filter rule was triggered
    match_found = (
        ma_response.sanitization_result.filter_match_state
        == modelarmor_v1.FilterMatchState.MATCH_FOUND
    )

    if match_found:
        logger.warning("Model Armor blocked prompt")
        logger.debug(f"Filter results: {dict(ma_response.sanitization_result.filter_results)}")
        return False
    else:
        logger.info("Model Armor prompt check passed")
        return True


def check_response_with_model_armor(
    model_response: str, project_id: str, model_armor_location: str, template_id: str
) -> bool:
    """
    Check model response against Model Armor template.

    Args:
        model_response: The model's output string
        project_id: GCP project ID
        model_armor_location: Model Armor service location (e.g., "us")
        template_id: Model Armor template ID for response validation

    Returns:
        True if the response is safe to proceed, False if it should be blocked
    """
    logger.info(f"Checking model response with Model Armor template: {template_id}")

    client = get_model_armor_client(model_armor_location)

    # Construct the resource name for the template
    template_name = client.template_path(project_id, model_armor_location, template_id)

    # Prepare the model response data object
    model_response_data = modelarmor_v1.DataItem(text=model_response)

    # Create the request for response sanitization
    ma_request = modelarmor_v1.SanitizeModelResponseRequest(
        name=template_name,
        model_response_data=model_response_data,
    )

    # Call the Model Armor service for response check
    ma_response = client.sanitize_model_response(request=ma_request)

    # Check the result. MATCH_FOUND means a filter rule was triggered
    match_found = (
        ma_response.sanitization_result.filter_match_state
        == modelarmor_v1.FilterMatchState.MATCH_FOUND
    )

    if match_found:
        logger.warning("Model Armor blocked response")
        logger.debug(f"Filter results: {dict(ma_response.sanitization_result.filter_results)}")
        return False
    else:
        logger.info("Model Armor response check passed")
        return True
