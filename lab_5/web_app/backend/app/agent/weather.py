"""Weather tools for the agent using Google Maps and NOAA APIs."""

import googlemaps
import requests
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def get_lat_long_from_city(
    city: str, state: str, google_api_key: str
) -> Optional[Tuple[float, float]]:
    """
    Convert city and state to latitude and longitude using Google Maps API.

    Args:
        city: City name (e.g., "Denver")
        state: Two-letter state code (e.g., "CO")
        google_api_key: Google Maps API key

    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    try:
        gmaps = googlemaps.Client(key=google_api_key)
        address = f"{city}, {state}, USA"

        # Geocode the address
        geocode_result = gmaps.geocode(address)
        logger.info(f"Geocoding result for {city}, {state}: {len(geocode_result) if geocode_result else 0} results")

        if geocode_result:
            location = geocode_result[0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            logger.warning(f"Geocoding returned 0 results for {city}, {state}")
            return None

    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API Error: {e}, Status: {e.status}, Message: {e.message}")
        return None
    except Exception as e:
        logger.error(f"Error geocoding {city}, {state}: {e}")
        return None


def get_grid_points(
    latitude: float, longitude: float, user_agent: str
) -> Optional[Tuple[str, int, int]]:
    """
    Get NOAA weather forecast office (WFO) and grid points from coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        user_agent: User-Agent header for NOAA API

    Returns:
        Tuple of (WFO, grid_x, grid_y) or None if request fails
    """
    try:
        # Round to avoid handling redirect from API with less precision
        points_url = f"https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}"
        headers = {"User-Agent": user_agent}

        response = requests.get(points_url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        properties = data["properties"]

        wfo = properties["cwa"]
        grid_x = properties["gridX"]
        grid_y = properties["gridY"]

        logger.info(f"Grid points retrieved: WFO={wfo}, GridX={grid_x}, GridY={grid_y}")
        return wfo, grid_x, grid_y

    except requests.exceptions.HTTPError as err:
        logger.error(f"NOAA API failed (HTTP Error): {err}")
        return None
    except Exception as e:
        logger.error(f"Error getting grid points: {e}")
        return None


def get_todays_forecast(wfo: str, grid_x: int, grid_y: int, user_agent: str) -> Optional[str]:
    """
    Get today's weather forecast from NOAA.

    Args:
        wfo: Weather forecast office identifier
        grid_x: Grid X coordinate
        grid_y: Grid Y coordinate
        user_agent: User-Agent header for NOAA API

    Returns:
        Formatted forecast string or None if request fails
    """
    if not wfo or not grid_x or not grid_y:
        logger.error("Cannot fetch forecast without valid grid data")
        return None

    try:
        # Construct the final forecast URL
        forecast_url = f"https://api.weather.gov/gridpoints/{wfo}/{grid_x},{grid_y}/forecast"
        headers = {"User-Agent": user_agent}

        response = requests.get(forecast_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        periods = data["properties"]["periods"]

        if periods:
            # The first period is usually 'Today' or the current period
            today_forecast = periods[0]

            forecast = "\n--- ☀️ Today's Forecast ---"
            forecast += f"**Period:** {today_forecast['name']}"
            forecast += f"**Temperature:** {today_forecast['temperature']}°{today_forecast['temperatureUnit']}"
            forecast += f"**Wind:** {today_forecast['windSpeed']} from {today_forecast['windDirection']}"
            forecast += f"**Details:** {today_forecast['detailedForecast']}"

            logger.info(f"Forecast retrieved for {wfo}/{grid_x},{grid_y}")
            return forecast
        else:
            logger.warning("Forecast data is empty")
            return None

    except requests.exceptions.HTTPError as err:
        logger.error(f"NOAA API failed (HTTP Error): {err}")
        return None
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        return None


def get_weather_from_city_state(
    city: str, state: str, google_api_key: str, noaa_user_agent: str
) -> Optional[str]:
    """
    Retrieves the current weather forecast for a given city and state.

    This function first converts the city and state names into geographic
    coordinates (latitude and longitude). It then uses these coordinates
    to determine the National Weather Service (NWS) forecast office (WFO)
    and grid points. Finally, it fetches and returns today's forecast.

    Args:
        city: The name of the city (e.g., "Denver")
        state: The two-letter state abbreviation (e.g., "CO")
        google_api_key: Google Maps API key
        noaa_user_agent: User-Agent header for NOAA API

    Returns:
        Formatted forecast string or None if any step fails
    """
    logger.info(f"Getting weather for {city}, {state}")

    coordinates = get_lat_long_from_city(city, state, google_api_key)
    if not coordinates:
        return None

    latitude, longitude = coordinates
    grid_data = get_grid_points(latitude, longitude, noaa_user_agent)
    if not grid_data:
        return None

    wfo, grid_x, grid_y = grid_data
    string_forecast = get_todays_forecast(wfo, grid_x, grid_y, noaa_user_agent)

    logger.info(f"Weather retrieval complete for {city}, {state}")
    return string_forecast
