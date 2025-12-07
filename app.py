import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# ------------------------------
# Safe font loader
# ------------------------------
def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


# ------------------------------
# Draw title using bbox
# ------------------------------
def draw_title(draw, W, text):
    font = load_font(80)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    draw.text(((W - tw) / 2, 50), text, font=font, fill="white")


# ------------------------------
# Draw weather info
# ------------------------------
def draw_weather(draw, W, H, weather):
    font = load_font(40)

    text = f"{weather['city']} | {weather['temp']}°C | {weather['description']}"

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]

    draw.text(((W - tw) / 2, H - 120), text, font=font, fill="white")


# ------------------------------
# Generate poster
# ------------------------------
def generate_poster(weather, width, height):
    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Title
    draw_title(draw, width, "Weather Poster")

    # Weather info
    draw_weather(draw, width, height, weather)

    return img


# -----------------------------------------
# Streamlit UI
# -----------------------------------------
st.set_page_config(page_title="Weather Poster", layout="wide")

st.title("🌤️ Weather-Driven Generative Poster")

width = st.slider("Poster Width", 400, 2000, 800)
height = st.slider("Poster Height", 400, 2000, 1000)

if st.button("Generate Poster"):
    try:
        # Fake weather data (you can replace this with API)
        weather = {
            "city": "Seoul",
            "temp": 5,
            "description": "Clear Sky"
        }

        poster = generate_poster(weather, width, height)
        st.image(poster, caption="Generated Poster")

    except Exception as e:
        st.error(f"Error: {e}")
