import streamlit as st
import requests
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import io

# -------------------------
# Weather → Color Mapping
# -------------------------
WEATHER_COLOR_MAP = {
    "sunny":  ("#FFB300", "#FF6F00"),     # bright warm yellow / orange
    "cloudy": ("#9E9E9E", "#616161"),     # gray tones
    "rain":   ("#4FC3F7", "#0288D1"),     # rain blues
    "snow":   ("#E1F5FE", "#B3E5FC"),     # soft icy blues
    "storm":  ("#455A64", "#263238"),     # dark stormy tones
    "fog":    ("#CFD8DC", "#B0BEC5"),
}

# -------------------------
# Detect weather category
# -------------------------
def classify_weather(weather_code):
    # Weather codes from Open-Meteo
    if weather_code in [0, 1]:
        return "sunny"
    if weather_code in [2, 3]:
        return "cloudy"
    if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "rain"
    if weather_code in [71, 73, 75, 77, 85, 86]:
        return "snow"
    if weather_code in [95, 96, 99]:
        return "storm"
    if weather_code in [45, 48]:
        return "fog"
    return "cloudy"

# -------------------------
# Get weather from Open-Meteo API
# -------------------------
def get_weather(city):
    try:
        # Geocoding API to get coordinates
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        ).json()

        if "results" not in geo:
            return None, None

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        # Get actual weather
        weather_data = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        ).json()

        weather_code = weather_data["current_weather"]["weathercode"]
        return weather_code, weather_data
    except:
        return None, None

# -------------------------
# Generate artistic poster
# -------------------------
def generate_poster(city, weather_category):
    # Base image - large for clarity
    width = 900
    height = 1400
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Pick color by weather
    c1, c2 = WEATHER_COLOR_MAP[weather_category]

    # Strong graphic gradient
    for y in range(height):
        ratio = y / height
        r = int(int(c1[1:3], 16) * (1 - ratio) + int(c2[1:3], 16) * ratio)
        g = int(int(c1[3:5], 16) * (1 - ratio) + int(c2[3:5], 16) * ratio)
        b = int(int(c1[5:7], 16) * (1 - ratio) + int(c2[5:7], 16) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Random abstract shapes for uniqueness
    for _ in range(10):
        shape_type = random.choice(["circle", "rect"])

        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = x1 + random.randint(150, 400)
        y2 = y1 + random.randint(150, 400)

        shape_color = tuple(np.random.randint(0, 255, 3))

        if shape_type == "circle":
            draw.ellipse([x1, y1, x2, y2], fill=shape_color + (80,))
        else:
            draw.rectangle([x1, y1, x2, y2], fill=shape_color + (80,))

    # Text layout: strong typography design
    try:
        font_city = ImageFont.truetype("arial.ttf", 120)
        font_weather = ImageFont.truetype("arial.ttf", 60)
    except:
        # fallback
        font_city = ImageFont.load_default()
        font_weather = ImageFont.load_default()

    draw.text((60, 60), city.upper(), fill="white", font=font_city)
    draw.text((60, 220), f"Weather: {weather_category}", fill="white", font=font_weather)

    # Apply grain texture for design feel
    grain = np.random.normal(0, 25, (height, width, 3)).astype(np.int16)
    img_np = np.array(img).astype(np.int16)
    img_np = np.clip(img_np + grain, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)

    return img


# -------------------------
# Streamlit UI
# -------------------------
st.title("City Weather Design Poster Generator")
st.write("Generates a unique high-design poster for each city based on real-time weather.")

city = st.text_input("Enter a city name", "Seoul")

if st.button("Generate Poster"):
    code, raw = get_weather(city)

    if code is None:
        st.error("City not found or weather API error.")
    else:
        category = classify_weather(code)
        poster = generate_poster(city, category)

        st.image(poster, caption=f"{city} – {category} weather", use_column_width=True)

        # Download button
        buf = io.BytesIO()
        poster.save(buf, format="PNG")
        st.download_button("Download Poster", buf.getvalue(), file_name=f"{city}_poster.png")
