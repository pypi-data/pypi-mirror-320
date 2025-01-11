import requests
import json


def get_weather_data(place, api_key=None):
    if not api_key:
        return None

    if not place:
        return None

    try:
        # Формируем запрос к OpenWeatherMap API
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": place,
                "appid": api_key,
                "units": "metric"
            }
        )
        response.raise_for_status()

        data = response.json()

        # Форматируем временную зону
        timezone_offset = data.get("timezone", 0) // 3600
        timezone = f"UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset}"

        # Формируем JSON-объект для вывода
        result = {
            "name": data.get("name"),
            "coord": data.get("coord", {}),
            "country": data.get("sys", {}).get("country"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "timezone": timezone
        }

        return json.dumps(result)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except KeyError as e:
        print(f"Key error in response: {e}")
        return None
