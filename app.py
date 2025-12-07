import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# =========================
#   Font Loader
# =========================
def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


# =========================
#   Weather API Function
# =========================
def fetch_weather(city, api_key):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={api_key}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    return {
        "city": city,
        "temp": data["main"]["temp"],
        "description": data["weather"][0]["description"].title(),
    }


# =========================
#   Draw Title
# =========================
def draw_title(draw, W, text):
    font = load_font(80)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 50), text, font=font, fill="white")


# =========================
#   Draw Weather Text
# =========================
def draw_weather(draw, W, H, weather):
    font = load_font(40)
    text = f"{weather['city']} | {weather['temp']}°C | {weather['description']}"

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]

    draw.text(((W - tw) / 2, H - 120), text, font=font, fill="white")


# =========================
#   Generate Poster
# =========================
def generate_poster(weather, width, height):
    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    draw_title(draw, width, "Weather Poster")
    draw_weather(draw, width, height, weather)

    return img


# =========================
#   Streamlit UI
# =========================
st.set_page_config(page_title="Weather Poster", layout="wide")

st.title("🌤️ Weather-Driven Generative Poster")

api_key = st.text_input("Enter your OpenWeather API Key")
city = st.text_input("City Name", "Seoul")

width = st.slider("Poster Width", 400, 2000, 800)
height = st.slider("Poster Height", 400, 2000, 1000)

if st.button("Generate Poster"):
    if not api_key:
        st.error("❗ Please enter your OpenWeather API key.")
    else:
        try:
            weather = fetch_weather(city, api_key)
            poster = generate_poster(weather, width, height)
            st.image(poster, caption="Generated Poster")

        except Exception as e:
            st.error(f"Error: {e}")
