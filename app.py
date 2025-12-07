import streamlit as st
import requests
import random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io

# -----------------------------
# Weather → Search Keyword
# -----------------------------
WEATHER_KEYWORD = {
    "Clear": "sunny",
    "Clouds": "cloudy",
    "Rain": "rainy",
    "Drizzle": "drizzle",
    "Thunderstorm": "storm",
    "Snow": "snow",
    "Mist": "mist",
    "Fog": "fog"
}

# -----------------------------
# Get Weather from OpenWeather
# -----------------------------
def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    data = requests.get(url).json()

    if data.get("cod") != 200:
        return None, None

    weather_type = data["weather"][0]["main"]
    return weather_type, data

# -----------------------------
# Get Photo from Unsplash
# -----------------------------
def get_photo(city, weather, unsplash_key):
    keyword = WEATHER_KEYWORD.get(weather, "city")
    query = f"{city} {keyword}"

    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={unsplash_key}&orientation=portrait"

    data = requests.get(url).json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    # Randomly choose one image for uniqueness
    photo_url = random.choice(data["results"])["urls"]["regular"]
    img = Image.open(requests.get(photo_url, stream=True).raw)
    return img


# -----------------------------
# Add subtle grain + overlay
# -----------------------------
def stylize(img):
    img = img.resize((900, 1400))

    # Light grain
    np_img = np.array(img).astype(np.int16)
    grain = np.random.normal(0, 10, np_img.shape).astype(np.int16)
    np_img = np.clip(np_img + grain, 0, 255).astype(np.uint8)
    img = Image.fromarray(np_img)

    # Transparent overlay for artistic feel
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 20))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    return img.convert("RGB")


# -----------------------------
# Streamlit Interface
# -----------------------------
st.title("Realistic City Weather Image Generator")
st.write("Enter your API keys to generate a unique real-world photo for each city.")

ow_key = st.text_input("OpenWeather API Key", type="password")
unsplash_key = st.text_input("Unsplash API Key", type="password")
city = st.text_input("City Name", "Seoul")

if st.button("Generate Image"):
    if not ow_key or not unsplash_key:
        st.error("Please enter both OpenWeather and Unsplash API keys.")
    else:
        weather_type, raw = get_weather(city, ow_key)

        if weather_type is None:
            st.error("City not found or wrong API key.")
        else:
            img = get_photo(city, weather_type, unsplash_key)

            if img is None:
                st.error("No matching images found on Unsplash.")
            else:
                final_img = stylize(img)

                st.image(final_img, caption=f"{city} – {weather_type} Weather")

                buf = io.BytesIO()
                final_img.save(buf, format="PNG")
                st.download_button("Download Image", buf.getvalue(), file_name=f"{city}_weather.png")
