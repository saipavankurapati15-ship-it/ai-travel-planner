from flask import Flask, render_template, request
import requests
from google import genai

app = Flask(__name__)

WEATHER_API_KEY = "b8699870cf0e2e7b4ad263d19afbdc7d"
GEOAPIFY_API_KEY = "d75eff4f03704c1cb0b1004013a05603"
GEMINI_API_KEY = "AQ.Ab8RN6JvYUWwIIlinsgWRqIDVnXqamdRf0sIhgoIWNqyvnlcNA"
client = genai.Client(api_key=GEMINI_API_KEY)


def get_coordinates(city):
    try:
        url = "https://api.geoapify.com/v1/geocode/search"

        params = {
            "text": city,
            "apiKey": GEOAPIFY_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("features"):
            lat = data["features"][0]["properties"]["lat"]
            lon = data["features"][0]["properties"]["lon"]
            return lat, lon

    except Exception as e:
        print("Coordinate Error:", e)

    return None, None


def get_weather(city):

    try:

        lat, lon = get_coordinates(city)

        if lat is None:
            return {
                "temp": "N/A",
                "condition": "Not Available",
                "humidity": "N/A"
            }

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        data = response.json()

        return {
            "temp": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }

    except Exception as e:

        print("Weather Error:", e)

        return {
            "temp": "N/A",
            "condition": "Not Available",
            "humidity": "N/A"
        }


def get_places(category, city):

    try:

        lat, lon = get_coordinates(city)

        if lat is None:
            return []

        url = "https://api.geoapify.com/v2/places"

        params = {
            "categories": category,
            "filter": f"circle:{lon},{lat},50000",
            "bias": f"proximity:{lon},{lat}",
            "limit": 10,
            "apiKey": GEOAPIFY_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        results = []

        for item in data.get("features", []):

            props = item.get("properties", {})
            name = props.get("name")

            if not name:
                continue

            lat2 = props.get("lat")
            lon2 = props.get("lon")

            results.append({
                "name": name,
                "map": f"https://www.google.com/maps/search/?api=1&query={lat2},{lon2}"
            })

        return results

    except Exception as e:
        print("Places Error:", e)
        return []


def get_ai_tourist_places(city):

    try:

        prompt = f"""
List exactly 10 famous tourist places in {city}.

Rules:
- One place per line
- No numbering
- No descriptions
- Only place names
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        print("GEMINI RESPONSE:")
        print(response.text)

        places = []

        for line in response.text.split("\n"):

            place = line.strip()

            if not place:
                continue

            place = (
                place.replace("-", "")
                .replace("*", "")
                .replace(".", "")
                .strip()
            )

            places.append({
                "name": place,
                "map": f"https://www.google.com/maps/search/{place}"
            })

        return places

    except Exception as e:

        print("Gemini Tourist Error:", e)

        return []
def get_ai_plan(destination, days, budget):

    return f"""
    <h3>Trip Plan for {destination}</h3>

    <p><b>Duration:</b> {days} Days</p>

    <p><b>Budget:</b> ₹{budget}</p>

    <h4>Day 1</h4>
    <p>Explore famous tourist attractions.</p>

    <h4>Day 2</h4>
    <p>Visit local markets and restaurants.</p>

    <h4>Day 3</h4>
    <p>Enjoy sightseeing and photography spots.</p>

    <h4>Travel Tips</h4>

    <ul>
        <li>Carry water bottle</li>
        <li>Keep ID proof</li>
        <li>Book hotels early</li>
        <li>Use Google Maps</li>
    </ul>
    """
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/result")
def result():

    source = request.args.get("source")
    destination = request.args.get("destination")
    budget = request.args.get("budget")
    days = request.args.get("days")

    weather = get_weather(destination)

    places = get_ai_tourist_places(destination)

    hotels = get_places(
        "accommodation.hotel",
        destination
    )

    restaurants = get_places(
        "catering.restaurant",
        destination
    )

    ai_plan = get_ai_plan(
        destination,
        days,
        budget
    )
    print("PLACES =", places)
    print("HOTELS =", hotels)
    print("RESTAURANTS =", restaurants)
    return render_template(
        "result.html",
        source=source,
        destination=destination,
        budget=budget,
        days=days,
        weather=weather,
        places=places,
        hotels=hotels,
        restaurants=restaurants,
        ai_plan=ai_plan
    )


if __name__ == "__main__":
    app.run(debug=True)