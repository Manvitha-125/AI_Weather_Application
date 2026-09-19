"""Groq integration for concise, evidence-based weather summaries."""

from typing import Any

from groq import Groq


class GroqServiceError(Exception):
    pass


def get_weather_explanation(weather: dict[str, Any], api_key: str) -> str:
    """Create a friendly explanation using only the supplied weather data."""
    if not api_key:
        raise GroqServiceError("Groq is not configured.")

    prompt = (
        "Explain these current weather conditions in 2 short, friendly sentences. "
        "Use only the facts below. You may give a practical clothing or umbrella suggestion, "
        "but do not make health, safety, forecast, or emergency claims.\n\n"
        f"Location: {weather['city']}, {weather['country']}\n"
        f"Condition: {weather['description']}\n"
        f"Temperature: {weather['temperature']}°C (feels like {weather['feels_like']}°C)\n"
        f"Humidity: {weather['humidity']}%\n"
        f"Wind speed: {weather['wind_speed']} km/h"
    )

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise, helpful weather assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        explanation = completion.choices[0].message.content
        if not explanation:
            raise GroqServiceError("Groq returned an empty explanation.")
        return explanation.strip()
    except GroqServiceError:
        raise
    except Exception as error:
        raise GroqServiceError("Unable to generate the AI explanation.") from error
