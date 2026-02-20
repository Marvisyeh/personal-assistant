import requests
from langchain.tools import tool

class WeatherTool:
  def __init__(self, latitude: float=25.037518, longitude: float=121.563661):
    self.url = "https://api.open-meteo.com/v1/forecast"
    self.params = {
      "forecast_days": 1,
      "latitude": latitude,
      "longitude": longitude,
      "daily": [
        "weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", 
        "rain_sum", "wind_speed_10m_max", "sunrise", "sunset", "daylight_duration", "sunshine_duration", 
        "uv_index_max", "uv_index_clear_sky_max", "wind_direction_10m_dominant", "wind_gusts_10m_max", 
        "shortwave_radiation_sum", "et0_fao_evapotranspiration", "precipitation_probability_max", "precipitation_hours", 
        "snowfall_sum", "precipitation_sum", "showers_sum"
      ]
    }
  
  def get_weather(self):
    return requests.get(self.url, params=self.params).json()

@tool
def get_weather(latitude: float, longitude: float) -> str:
  """Get the weather for a given latitude and longitude"""
  weather = WeatherTool(latitude=latitude, longitude=longitude)
  return weather.get_weather()

if __name__ == "__main__":
  tpe_latitude = 25.037518
  tpe_longitude = 121.563661
  weather = WeatherTool(latitude=tpe_latitude, longitude=tpe_longitude)
  print(weather.get_weather())


