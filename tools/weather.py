# tools/weather.py

import os
import requests
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Fetches the current weather for a specified city. Use this for any questions about weather."""
    print(f"--- Calling Weather Tool for city: {city} ---")
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not api_key:
        print("--- Weather Tool Error: API key not found ---")
        return "Error: OpenWeatherMap API key not found."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "imperial"}

    try:
        response = requests.get(base_url, params=params)
        print(f"--- Weather API Response Status: {response.status_code} ---")
        
        # Specifically check for an invalid API key error (401)
        if response.status_code == 401:
            print("--- Weather Tool Error: Invalid API Key ---")
            return "Error: The OpenWeatherMap API key is invalid. Please check your .env file."
        
        response.raise_for_status()  # Check for other errors like 404 (city not found)
        data = response.json()
        
        city_name = data["name"]
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        
        result = f"The current weather in {city_name} is {temp}°F with {description}."
        print(f"--- Weather Tool Success: {result} ---")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"--- Weather Tool Error: Network issue - {e} ---")
        return f"Error: Could not connect to the weather service."
    except KeyError:
        print(f"--- Weather Tool Error: Could not parse response for {city} ---")
        return f"Error: Could not find weather data for {city}. Please check the city name."