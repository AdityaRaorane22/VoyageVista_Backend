import requests, os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(destination: str):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": round(data["main"]["temp"]),
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["main"],
                "windSpeed": round(data["wind"]["speed"] * 3.6)
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return None
