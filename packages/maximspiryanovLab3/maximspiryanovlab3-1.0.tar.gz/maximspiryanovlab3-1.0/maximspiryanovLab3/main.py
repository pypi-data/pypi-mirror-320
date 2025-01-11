from owm_key import owm_api_key
from getweatherdata import get_weather_data
import json

def fetch_weather_data_for_cities(cities):
    """
    Получает данные о погоде для списка городов.

    :param cities: Список городов.
    :return: Словарь с городами и их погодными данными.
    """
    print("it works!")
    results = {}
    for city in cities:
        print(f"Fetching weather data for {city}...")
        weather_data = get_weather_data(city, api_key=owm_api_key)

        if weather_data:
            results[city] = json.loads(weather_data)
        else:
            print(f"Failed to fetch weather data for {city}")
            results[city] = None
    return results

if __name__ == '__main__':
    cities = ["Moscow", "Chicago", "Dhaka"]
    weather_results = fetch_weather_data_for_cities(cities)
    print(json.dumps(weather_results, indent=4, ensure_ascii=False))
