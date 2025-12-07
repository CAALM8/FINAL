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
# Get real photo from Pexels API
# ---------------------------
def get_weather_photo(condition, pexels_key):
    keyword = "weather"

    if "clear" in condition.lower():
        keyword = "sunny sky"
    elif "cloud" in condition.lower():
        keyword = "cloudy sky"
    elif "rain" in condition.lower():
        keyword = "rain storm"
    elif "snow" in condition.lower():
        keyword = "snow landscape"
    elif "fog" in condition.lower() or "mist" in condition.lower():
        keyword = "fog landscape"
    elif "thunder" in condition.lower():
        keyword = "thunderstorm"

    headers = {
        "Authorization": pexels_key
    }

    search_url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=1"
    res = requests.get(search_url, headers=headers).json()

    if "photos" not in res or len(res["photos"]) == 0:
        raise Exception("No image found")

    img_url = res["photos"][0]["src"]["large"]

    img_data = requests.get(img_url).content
    return Image.open(BytesIO(img_data))


# ---------------------------
# Generate Final Poster
# ---------------------------
def generate_poster(weather, city, width, height, pexels_key):
    condition = weather["weather"][0]["description"]
    temperature = weather["main"]["temp"]

    background = get_weather_photo(condition, pexels_key)
    background = background.resize((width, height))

    draw = ImageDraw.Draw(background)

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_text = ImageFont.truetype("arial.ttf", 32)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Text
    text_title = "Weather Poster"
    text_info = f"{city} | {temperature}°C | {condition.capitalize()}"

    draw.text((40, 40), text_title, font=font_title, fill="white")
    draw.text((40, height - 80), text_info, font=font_text, fill="white")

    return background


# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🌤 Realistic Weather Poster Generator (Pexels Version)")

weather_key = st.text_input("Enter your OpenWeather API Key")
pexels_key = st.text_input("Enter your FREE Pexels API Key")
city = st.text_input("City Name", "Seoul")

width = st.slider("Poster Width", 600, 1600, 900)
height = st.slider("Poster Height", 600, 1600, 1200)

if st.button("Generate Poster"):
    if not weather_key or not pexels_key:
        st.error("Please enter ALL API keys.")
    else:
        with st.spinner("Generating Image..."):
            weather = get_weather(weather_key, city)

            if "weather" not in weather:
                st.error("City not found or API error.")
            else:
                poster_img = generate_poster(weather, city, width, height, pexels_key)

                buf = BytesIO()
                poster_img.save(buf, format="PNG")
                st.image(buf.getvalue(), use_column_width=True)

                st.download_button(
                    "Download Poster",
                    buf.getvalue(),
                    file_name="weather_poster.png",
                    mime="image/png"
                )
