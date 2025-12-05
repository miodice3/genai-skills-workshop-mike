"""Core agent logic for Google GenAI with RAG and weather tools."""

from google import genai
from google.genai import types
import logging
from typing import Optional

from app.config import get_settings
from app.agent.weather import get_weather_from_city_state
from app.agent.model_armor import (
    check_prompt_with_model_armor,
    check_response_with_model_armor,
)

logger = logging.getLogger(__name__)


def handle_response(
    client: genai.Client,
    response: types.GenerateContentResponse,
    contents: list,
    config: types.GenerateContentConfig,
    model: str,
) -> Optional[str]:
    """
    Recursively handle model responses, executing function calls as needed.

    Args:
        client: GenAI client instance
        response: Model response to process
        contents: Conversation history (mutable list)
        config: Generation configuration
        model: Model name

    Returns:
        Final text response or None
    """
    settings = get_settings()

    # 1. Check for function calls
    function_call_part = None
    # Iterate to find the specific part containing the function call
    if (
        response.candidates
        and response.candidates[0].content
        and response.candidates[0].content.parts
    ):
        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_call_part = part
                break

    if function_call_part:
        function_obj = function_call_part.function_call

        # CRITICAL: Capture the Call ID
        # The API requires this ID to match the response later
        call_id = getattr(function_obj, "id", None)

        logger.info(f"Model requested function: {function_obj.name}, Call ID: {call_id}")

        result_part = None

        if function_obj.name == "get_weather_from_city_state":
            try:
                # Extract arguments
                args = function_obj.args
                city = args.get("city")
                state = args.get("state")

                # Execute weather function
                result_output = get_weather_from_city_state(
                    city, state, settings.google_api_key, settings.noaa_user_agent
                )
                logger.info(f"Weather tool executed for {city}, {state}")

                # Construct the tool response
                result_part = types.Part(
                    function_response=types.FunctionResponse(
                        name="get_weather_from_city_state",
                        response={"content": result_output},  # Must be a dict
                        id=call_id,  # Pass the ID back
                    )
                )
            except Exception as e:
                logger.error(f"Error executing weather tool: {e}")

        if not result_part:
            logger.error("No result generated from tool execution")
            return None

        # Sanitize the model's turn in history
        # Reconstruct a clean FunctionCall object to prevent 400 errors
        clean_function_call = types.FunctionCall(
            name=function_obj.name, args=function_obj.args, id=call_id
        )

        sanitized_model_turn = types.Content(
            role="model", parts=[types.Part(function_call=clean_function_call)]
        )
        contents.append(sanitized_model_turn)

        # Append the tool response (role="tool")
        tool_turn = types.Content(role="tool", parts=[result_part])
        contents.append(tool_turn)

        logger.info("Recursively calling model with updated history")

        # Recursive call
        try:
            # Remove retrieval tool from config for subsequent calls
            config.tools = config.tools[1:]

            next_response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            logger.info("Recursive model call completed, handling response")
            return handle_response(client, next_response, contents, config, model)
        except Exception as e:
            logger.error(f"API Error during recursion: {e}")
            return None

    else:
        # Base case: Text response
        logger.info("Final response received from model")
        if response.text:
            return response.text
        return None


def generate(user_query: str) -> Optional[str]:
    """
    Main entry point for generating responses using the GenAI agent.

    This function:
    1. Validates the user prompt with Model Armor
    2. Calls the Gemini model with RAG and weather tools
    3. Handles function calls recursively
    4. Validates the final response with Model Armor

    Args:
        user_query: User's input question

    Returns:
        Final response text or None if blocked by Model Armor
    """
    settings = get_settings()

    logger.info(f"Processing query: {user_query[:50]}...")

    # 1. Initialize Client
    client = genai.Client(vertexai=True)

    model = settings.model_name

    system_instructions = """You are a helpful AI assistant with access to weather information and knowledge retrieval capabilities for the Alaska Department of Snow.
  When users ask about weather, use the get_weather_from_city_state function to get accurate, current forecasts.
  For other questions, you can search through your knowledge base to provide helpful information.

  RULES:
  1. if a user asks about anything other than a weather forecast in a City and State, snow, or Alaska Department of Snow, respond with "I'm sorry I cannot help you with that."
  2. Limit your final response to 240 characters or less.
  3. Add the relevant hash tag in ALL CAPITAL LETTERS, #FORECAST, #ALASKA_DS, #USEANOTHERCHATBOT

  User Query:
  """

    enhanced_user_query = system_instructions + user_query

    # 2. Define Contents (Mutable list for history)
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_query)]),
    ]

    # 3. Define Function Calling Tool (Weather)
    logger.info("Defining Function Calling Tool (Weather)")
    weather_tool_declaration = types.FunctionDeclaration(
        name="get_weather_from_city_state",
        description="""Retrieves the current weather forecast for a given city and state.

  This function first converts the city and state names into geographic
  coordinates (latitude and longitude). It then uses these coordinates
  to determine the National Weather Service (NWS) forecast office (WFO)
  and grid points. Finally, it fetches and returns today's forecast.

  Args:
      city: The name of the city (e.g., "Denver")
      state: The two-letter state abbreviation (e.g., "CO")

  Returns:
      Formatted forecast string or None if any step fails
  """,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "city": types.Schema(
                    type=types.Type.STRING, description="The name of the city, e.g., 'Denver'."
                ),
                "state": types.Schema(
                    type=types.Type.STRING,
                    description="The two-letter abbreviation for the state, e.g., 'CO'.",
                ),
            },
            required=["city", "state"],
        ),
    )

    # Tool object for function calling
    x_weather_tool = types.Tool(function_declarations=[weather_tool_declaration])
    logger.info("Function Calling Tool defined")

    # 4. Define Retrieval Tool (RAG)
    logger.info("Defining Retrieval Tool (RAG)")
    retrieval_tool = types.Tool(
        retrieval=types.Retrieval(
            vertex_rag_store=types.VertexRagStore(
                rag_resources=[
                    types.VertexRagStoreRagResource(rag_corpus=settings.rag_corpus)
                ],
            )
        )
    )
    logger.info("Retrieval Tool defined")

    # 5. Define GenerateContentConfig
    logger.info("Defining GenerateContentConfig with combined tools list")
    all_tools = [retrieval_tool, x_weather_tool]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=65535,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        tools=all_tools,
    )
    logger.info("GenerateContentConfig defined")

    # 6. Check prompt with Model Armor
    logger.info("Checking prompt with Model Armor")
    if not check_prompt_with_model_armor(
        user_query,
        settings.project_id,
        settings.model_armor_location,
        settings.model_armor_template_id,
    ):
        logger.warning("Prompt blocked by Model Armor")
        return None

    # 7. Call generate_content (initial call)
    logger.info("Calling generate_content (Initial Call)")
    try:
        initial_response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        logger.info("Initial response received")

        # 8. Start the recursive handling process
        final_response = handle_response(
            client, initial_response, contents, generate_content_config, model
        )

        if not final_response:
            logger.warning("No final response generated")
            return None

        logger.info("Checking final response with Model Armor")

        # 9. Check response with Model Armor
        is_response_safe = check_response_with_model_armor(
            final_response,
            settings.project_id,
            settings.model_armor_location,
            settings.model_armor_response_template_id,
        )

        if is_response_safe:
            logger.info("Response passed Model Armor")
            return final_response
        else:
            logger.warning("Response blocked by Model Armor")
            return None

    except Exception as e:
        logger.error(f"Error during generation: {e}")
        return None
