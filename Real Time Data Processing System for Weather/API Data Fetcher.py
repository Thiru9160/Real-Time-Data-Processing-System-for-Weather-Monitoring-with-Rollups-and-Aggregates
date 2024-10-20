import requests
import time

API_KEY = '7340f40a4c20fa7a39eaabf0e3415608'
CITY_IDS = {'Delhi': 1273294, 'Mumbai': 1275339, 'Chennai': 1264527, 'Bangalore': 1277333, 'Kolkata': 1275004, 'Hyderabad': 1269843}
INTERVAL = 300  # 5 minutes

def fetch_weather(city_id):
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

def kelvin_to_celsius(temp_kelvin):
    return temp_kelvin - 273.15

def process_weather_data(data):
    temp_kelvin = data['main']['temp']
    temp_celsius = kelvin_to_celsius(temp_kelvin)
    feels_like_celsius = kelvin_to_celsius(data['main']['feels_like'])
    weather_condition = data['weather'][0]['main']
    timestamp = data['dt']
    return {
        'temperature': temp_celsius,
        'feels_like': feels_like_celsius,
        'condition': weather_condition,
        'timestamp': timestamp
    }

def monitor_weather():
    while True:
        for city, city_id in CITY_IDS.items():
            weather_data = fetch_weather(city_id)
            processed_data = process_weather_data(weather_data)
            # Store data in DB
            print(f"Weather in {city}: {processed_data}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    monitor_weather()
