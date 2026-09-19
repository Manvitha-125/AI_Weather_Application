import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from services.groq_service import GroqServiceError, get_weather_explanation
from services.weather_service import WeatherServiceError, get_current_weather


load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.get("/")
def index():
    """Serve the weather search page."""
    return render_template("index.html")


@app.get("/api/weather")
def weather():
    """Return current weather and, when available, an AI explanation."""
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please enter a city name."}), 400
    if len(city) > 100:
        return jsonify({"error": "City name is too long."}), 400

    try:
        weather_data = get_current_weather(city, os.getenv("OPENWEATHER_API_KEY", ""))
    except WeatherServiceError as error:
        return jsonify({"error": str(error)}), error.status_code

    response = {"weather": weather_data, "ai_explanation": None, "ai_available": False}
    try:
        response["ai_explanation"] = get_weather_explanation(
            weather_data, os.getenv("GROQ_API_KEY", "")
        )
        response["ai_available"] = True
    except GroqServiceError:
        # Weather is still useful when Groq is not configured or is unavailable.
        response["ai_explanation"] = (
            "AI weather insight is unavailable right now. "
            "The current conditions are shown above."
        )

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
