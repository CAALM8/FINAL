import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import math
import requests

st.set_page_config(page_title="Weather-Driven Generative Poster", layout="wide")

# ---------------------------
# Weather API
# ---------------------------
def get_weather(lat=37.57, lon=126.98):  # Default: Seoul
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = requests.get(url)
    data = r.json()

    temp = data["current_weather"]["temperature"]
    wind = data["current_weather"]["windspeed"]
    code = data["current_weather"]["weathercode"]

    return temp, wind, code

# ---------------------------
# Color palettes
# ---------------------------
PALETTES = {
    "Warm": ["#ff6b6b", "#ffa36c", "#ffd93d", "#ffb5a7", "#f07167"],
    "Cool": ["#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f"],
    "Mono": ["#111111", "#444444", "#888888", "#cccccc", "#ffffff"],
}

# ---------------------------
# Draw noise line
# ---------------------------
def draw_noise(draw, width, height, color, strength):
    points = []
    for x in range(0, width, 10):
        y = int(height/2 + math.sin(x*0.04)*strength + random.randint(-strength, strength))
        points.append((x, y))
    draw.line(points, fill=color, width=3)

# ---------------------------
# Draw random rectangles
# ---------------------------
def draw_rectangles(draw, width, height, palette, count):
    for _ in range(count):
        w = random.randint(60, 240)
        h = random.randint(60, 240)
        x = random.randint(0, width - w)
        y = random.randint(0, height - h)
        color = random.choice(palette)
        draw.rectangle([x, y, x+w, y+h], fill=color)

# ---------------------------
# Draw title
# ---------------------------
def draw_title(draw, width, height, text):
    try:
        font = ImageFont.truetype("arial.ttf", 55)
    except:
        font = ImageFont.load_default()

    tw, th = draw.textsize(text, font=font)
    draw.text(((width - tw) / 2, height - th - 40), text, font=font, fill="white")

# ---------------------------
# Main generator
# ---------------------------
def generate_poster(weather, w, h):
    temp, wind, code = weather

    # Select palette based on temperature
    if temp < 10:
        palette_name = "Cool"
    else:
        palette_name = "Warm"

    palette = PALETTES[palette_name]

    img = Image.new("RGB", (w, h), random.choice(palette))
    draw = ImageDraw.Draw(img)

    # Rectangle count influenced by weather code
    rect_count = 5 + (code % 5)

    draw_rectangles(draw, w, h, palette, rect_count)
    draw_noise(draw, w, h, random.choice(palette), strength=int(wind * 4))

    title_text = f"Weather Poster — {temp}°C, {wind} m/s"
    draw_title(draw, w, h, title_text)

    return img

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🌤 Weather-Driven Generative Poster")

width = st.slider("Poster Width", 600, 1200, 800)
height = st.slider("Poster Height", 800, 1600, 1000)

if st.button("Generate Poster"):
    weather = get_weather()
    poster = generate_poster(weather, width, height)

    st.image(poster, caption="Generated Poster", use_column_width=True)

    poster.save("poster.png")
    with open("poster.png", "rb") as f:
        st.download_button(
            label="Download Poster",
            data=f,
            file_name="poster.png",
            mime="image/png",
        )
