import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

st.set_page_config(page_title="Realistic City Weather Image Generator", layout="centered")

# ----------- Weather → Keyword 映射 -----------
WEATHER_KEYWORD = {
    "Clear": "sunny",
    "Clouds": "cloudy",
    "Rain": "rainy",
    "Drizzle": "light rain",
    "Thunderstorm": "storm",
    "Snow": "snow",
    "Mist": "mist fog",
    "Fog": "fog",
    "Haze": "haze",
    "Smoke": "smoke",
}


# ----------- 获取城市天气 -----------
def get_weather(city, api_key):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={city}"
        f"&appid={api_key}&units=metric"
    )
    data = requests.get(url).json()

    if "weather" not in data:
        return None, None, None

    weather_type = data["weather"][0]["main"]
    country = data["sys"]["country"]
    temperature = data["main"]["temp"]
    return weather_type, country, temperature


# ----------- 获取城市图片（强 → 弱搜索链） -----------
def get_photo(city, weather, country, unsplash_key):
    keyword = WEATHER_KEYWORD.get(weather, "")

    search_list = [
        f"{city} {keyword}",
        f"{city} city",
        f"{country} city",
        city,
        "city skyline"
    ]

    for query in search_list:
        url = (
            f"https://api.unsplash.com/search/photos?"
            f"query={query}&client_id={unsplash_key}&orientation=portrait"
        )

        data = requests.get(url).json()

        if "results" in data and len(data["results"]) > 0:
            photo_url = random.choice(data["results"])["urls"]["regular"]
            img = Image.open(requests.get(photo_url, stream=True).raw)
            return img

    return None


# ----------- 生成带文字的最终海报 -----------
def generate_poster(img, city, country, temp, weather):
    img = img.resize((800, 1200))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()

    text = f"{city}, {country}\n{temp}°C | {weather}"
    draw.text((40, 40), text, fill="white", font=font)

    return img


# ======================= Streamlit UI ===========================
st.title("🌆 Realistic City Weather Image Generator")
st.write("Enter your API keys to generate a unique real-world photo for each city.")

open_key = st.text_input("OpenWeather API Key", type="password")
unsplash_key = st.text_input("Unsplash API Key", type="password")

city = st.text_input("City Name", "Seoul")


if st.button("Generate Image"):
    if not open_key or not unsplash_key:
        st.error("Please enter BOTH API keys.")
    else:
        st.info("Fetching weather...")

        weather_type, country, temp = get_weather(city, open_key)

        if not weather_type:
            st.error("City not found or API error.")
        else:
            st.info(f"Weather: {weather_type}, fetching image...")

            img = get_photo(city, weather_type, country, unsplash_key)

            if img is None:
                st.error("Could not fetch image. Please check Unsplash API Key.")
            else:
                poster = generate_poster(img, city, country, temp, weather_type)
                st.image(poster, caption="Generated Weather Image")

                # Download
                buf = BytesIO()
                poster.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="Download Image",
                    data=byte_im,
                    file_name=f"{city}_weather.png",
                    mime="image/png",
                )
