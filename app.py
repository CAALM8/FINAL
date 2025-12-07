import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


# ---------------------------
# Get weather data
# ---------------------------
def get_weather(api_key, city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()


# ---------------------------
# Get real photo based on weather condition
# ---------------------------
def get_weather_photo(condition):
    keyword = "weather"

    if "clear" in condition.lower():
        keyword = "clear sky"
    elif "cloud" in condition.lower():
        keyword = "cloudy sky"
    elif "rain" in condition.lower():
        keyword = "rainy weather"
    elif "snow" in condition.lower():
        keyword = "snow landscape"
    elif "fog" in condition.lower() or "mist" in condition.lower():
        keyword = "fog"
    elif "thunder" in condition.lower():
        keyword = "thunderstorm"

    # Unsplash 免费图片，无需 API Key
    img_url = f"https://source.unsplash.com/1600x900/?{keyword}"

    img_data = requests.get(img_url).content
    return Image.open(BytesIO(img_data))


# ---------------------------
# Generate final poster
# ---------------------------
def generate_poster(weather, city, width, height):
    condition = weather["weather"][0]["description"]
    temperature = weather["main"]["temp"]

    # Load background
    bg = get_weather_photo(condition)
    bg = bg.resize((width, height))

    draw = ImageDraw.Draw(bg)

    # Font
    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_text = ImageFont.truetype("arial.ttf", 32)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Draw text
    text_title = "Weather Poster"
    text_info = f"{city} | {temperature}°C | {condition.capitalize()}"

    draw.text((40, 40), text_title, font=font_title, fill="white")
    draw.text((40, height - 80), text_info, font=font_text, fill="white")

    return bg


# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🌤 Realistic Weather Poster Generator")

api_key = st.text_input("Enter your OpenWeather API Key")
city = st.text_input("City Name", "Seoul")

width = st.slider("Poster Width", 600, 1600, 900)
height = st.slider("Poster Height", 600, 1600, 1200)

if st.button("Generate Poster"):
    if not api_key:
        st.error("Please enter your OpenWeather API Key.")
    else:
        with st.spinner("Generating..."):
            weather = get_weather(api_key, city)

            if "weather" not in weather:
                st.error("City not found or API error.")
            else:
                poster_img = generate_poster(weather, city, width, height)

                buf = BytesIO()
                poster_img.save(buf, format="PNG")
                st.image(buf.getvalue(), use_column_width=True)

                st.download_button(
                    "Download Poster",
                    buf.getvalue(),
                    file_name="weather_poster.png",
                    mime="image/png"
                )
