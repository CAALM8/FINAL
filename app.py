import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

# ---------------------------
# Weather API
# ---------------------------
def get_weather(city, api_key):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={city}"
        f"&appid={api_key}&units=metric"
    )
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return None  # invalid city

    return {
        "city": city,
        "temp": response["main"]["temp"],
        "description": response["weather"][0]["description"],
    }


# ---------------------------
# Generate Realistic Background Image (OpenAI)
# ---------------------------
def generate_realistic_image(weather_text, openai_key):
    url = "https://api.openai.com/v1/images/generations"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}"
    }

    prompt = (
        f"Ultra-realistic landscape or city photograph showing the weather condition: {weather_text}. "
        "Natural light, cinematic photography, high detail, 4k aesthetic, atmospheric mood."
    )

    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024"
    }

    response = requests.post(url, json=payload, headers=headers).json()
    image_base64 = response["data"][0]["b64_json"]

    # Convert base64 → PIL image
    return Image.open(BytesIO(base64.b64decode(image_base64)))


# ---------------------------
# Draw Text Functions
# ---------------------------
def draw_title(draw, W, text):
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 40), text, font=font, fill="white")


def draw_weather(draw, W, H, weather):
    info = f"{weather['city']} | {weather['temp']}°C | {weather['description'].title()}"

    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), info, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, H - 120), info, font=font, fill="white")


# ---------------------------
# Generate Poster
# ---------------------------
def generate_poster(weather, width, height, openai_key):
    # Generate realistic weather image
    weather_text = f"{weather['description']} in {weather['city']}"
    bg = generate_realistic_image(weather_text, openai_key)
    bg = bg.resize((width, height))

    img = bg.copy()
    draw = ImageDraw.Draw(img)

    draw_title(draw, width, "Weather Poster")
    draw_weather(draw, width, height, weather)

    return img


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Weather Poster Generator", layout="centered")
st.title("🌤️ Weather-Driven Realistic Poster")

open_api = st.text_input("Enter your OpenWeather API Key")
openai_key = st.text_input("Enter your OpenAI API Key (for realistic image)")
city = st.text_input("City Name", "Seoul")

width = st.slider("Poster Width", 400, 1400, 800)
height = st.slider("Poster Height", 400, 1600, 1000)

if st.button("Generate Poster"):
    if not open_api or not openai_key:
        st.error("Please enter both API keys.")
    else:
        weather = get_weather(city, open_api)

        if weather is None:
            st.error("City not found. Try again.")
        else:
            st.success("Weather fetched! Generating AI poster...")
            poster = generate_poster(weather, width, height, openai_key)

            st.image(poster, caption="Generated Weather Poster")
            st.download_button(
                "Download Poster",
                data=poster_to_bytes := BytesIO(),
                file_name="weather_poster.png",
                mime="image/png",
            )
            poster.save(poster_to_bytes, format="PNG")
