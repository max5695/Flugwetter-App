from flask import Flask, request, render_template
import requests
from datetime import datetime



app = Flask(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_PARAMS = {
    "latitude": 0,   # Default latitude
    "longitude": 0,  # Default longitude
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
    "timezone": "Europe/Berlin"
}

CITIES = {
    "Berlin": {"lat": 52.52, "lon": 13.405},
    "Munich": {"lat": 48.1351, "lon": 11.582},
    "Hamburg": {"lat": 53.55, "lon": 10.0},
    "Cologne": {"lat": 50.93, "lon": 6.95},
    "Frankfurt": {"lat": 50.1109, "lon": 8.6821},
    "Stuttgart": {"lat": 48.7758, "lon": 9.1829},
    # Weitere Städte können hier hinzugefügt werden
}



def get_weather_data(city_coords, date):
    params = WEATHER_PARAMS.copy()
    params["latitude"] = city_coords["lat"]
    params["longitude"] = city_coords["lon"]
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        for day in weather_data["daily"]["time"]:
            if day == date:
                index = weather_data["daily"]["time"].index(day)
                return {
                    "temperature_max": weather_data["daily"]["temperature_2m_max"][index],
                    "temperature_min": weather_data["daily"]["temperature_2m_min"][index],
                    "precipitation": weather_data["daily"]["precipitation_sum"][index],
                    "windspeed_max": weather_data["daily"]["windspeed_10m_max"][index]
                }
    return None


def check_flight_conditions(start_weather, end_weather):
    if not start_weather or not end_weather:
        return "Wetterdaten für das ausgewählte Datum nicht verfügbar."
    
    conditions_ok = True
    reasons = []
    
    if start_weather["temperature_max"] < 0 or end_weather["temperature_max"] < 0:
        conditions_ok = False
        reasons.append("Temperatur unter 0°C")
        
    if start_weather["precipitation"] > 5 or end_weather["precipitation"] > 5:
        conditions_ok = False
        reasons.append("hoher Niederschlagsmenge")
        
    if start_weather["windspeed_max"] > 20 or end_weather["windspeed_max"] > 20:
        conditions_ok = False
        reasons.append("hoher Windgeschwindigkeit")
    
    if conditions_ok:
        return "Flugbedingungen sind gut."
    else:
        return f"Flug wird aufgrund von {', '.join(reasons)} nicht empfohlen."




@app.route("/", methods=["GET", "POST"])
def index():
    flight_status = None
    start_city = None
    end_city = None
    flight_date = None
    if request.method == "POST":
        start_city = request.form.get("start_city")
        end_city = request.form.get("end_city")
        flight_date = request.form.get("flight_date")
        if start_city and end_city and flight_date:
            start_weather = get_weather_data(CITIES[start_city], flight_date)
            end_weather = get_weather_data(CITIES[end_city], flight_date)
            flight_status = check_flight_conditions(start_weather, end_weather)
            
    return render_template("template.html", flight_status=flight_status, cities=CITIES.keys(), start_city=start_city, end_city=end_city, flight_date=flight_date)


if __name__ == "__main__":
    app.run()