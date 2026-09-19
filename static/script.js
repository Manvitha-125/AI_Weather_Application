const form = document.querySelector("#weather-form");
const cityInput = document.querySelector("#city-input");
const statusMessage = document.querySelector("#status");
const result = document.querySelector("#weather-result");
const submitButton = form.querySelector("button");

function setStatus(message, type = "") {
  statusMessage.textContent = message;
  statusMessage.className = `status ${type}`;
}

function showWeather(weather, explanation) {
  document.querySelector("#location").textContent = [weather.city, weather.country]
    .filter(Boolean)
    .join(", ");
  document.querySelector("#condition").textContent = weather.description;
  document.querySelector("#temperature").textContent = weather.temperature;
  document.querySelector("#feels-like").textContent = `Feels like ${weather.feels_like}°C`;
  document.querySelector("#humidity").textContent = `${weather.humidity}%`;
  document.querySelector("#wind-speed").textContent = `${weather.wind_speed} km/h`;
  document.querySelector("#ai-explanation").textContent = explanation;

  const icon = document.querySelector("#weather-icon");
  icon.src = `https://openweathermap.org/img/wn/${weather.icon}@2x.png`;
  icon.alt = `${weather.description} icon`;
  result.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const city = cityInput.value.trim();
  if (!city) {
    setStatus("Enter a city name to continue.", "error");
    cityInput.focus();
    return;
  }

  setStatus("Finding current conditions and preparing your insight…", "loading");
  result.hidden = true;
  submitButton.disabled = true;

  try {
    const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Unable to get weather right now.");

    showWeather(data.weather, data.ai_explanation);
    setStatus("");
  } catch (error) {
    setStatus(error.message || "Something went wrong. Please try again.", "error");
  } finally {
    submitButton.disabled = false;
  }
});
