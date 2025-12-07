import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

st.set_page_config(page_title="Realistic Weather Image Generator", layout="centered")

# ---------------- Weather Keywords -----------------
WEATHER_KEYWORD = {
    "Clear": "sunny",
    "Clouds": "cloudy sky",
    "Rain": "rainy streets",
    "Drizzle": "light rain",
    "Thunderstorm": "storm weather",
    "Snow": "snow city",
    "Mist": "mist fog",
    "Fog": "fog city",
    "Haze": "hazy sky",
    "Smoke": "smoky city"
}

# ---------------- Weather API -----------------
def get_weather(city, api_key):
    url = (f"https://api.openweathermap.org/data/2.5/weather?q={city}"
           f"&appid={api_key}&units=metric")
    data = requests.get(url).json()

    if "weather" not in data:
        return None, None, None

    weather_type = data["weather"][0]["main"]
    country = data["sys"]["country"]
    temperature = data["main"]["temp"]
    return weather_type, country, temperature


# ---------------- Unsplash API -----------------
def unsplash_search(query, key, page=1, orientation="portrait"):
    url = "https://api.unsplash.com/search/photos"
    headers = {"Accept-Version": "v1", "Authorization": f"Client-ID {key}"}

    params = {
        "query": query,
        "page": page,
        "per_page": 15,
        "orientation": orientation
    }

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    if "results" in data and len(data["results"]) > 0:
        return data["results"]
    return None


def get_photo(city, weather, country, unsplash_key):
    keyword = WEATHER_KEYWORD.get(weather, "")

    search_terms = [
        f"{city} {keyword}",
        f"{city} weather",
        f"{city} city view",
        f"{country} city",
        city,
        "urban landscape",
        "city skyline"
    ]

    orientations = ["portrait", "landscape", "squarish"]

    for query in search_terms:
        for orient in orientations:
            for page in range(1, 4):  # Try 3 pages for reliability
                results = unsplash_search(query, unsplash_key, page, orient)
                if results:
                    choice = random.choice(results)
                    url = choice["urls"]["regular"]
                    return Image.open(requests.get(url, stream=True).raw)

    return None


# ---------------- Poster Generate -----------------
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


# ---------------- SIDEBAR UI -----------------
st.sidebar.header("API Settings")

openweather_key = st.sidebar.text_input(
    "OpenWeather API Key",
    type="password",
    placeholder="Enter your OpenWeather Key"
)

unsplash_key = st.sidebar.text_input(
    "Unsplash API Key",
    type="password",
    placeholder="Enter your Unsplash Access Key"
)

# ---- How to get OpenWeather key ----
with st.sidebar.expander("How to get a free OpenWeather API Key"):
    st.markdown("""
### Steps to obtain OpenWeather API Key:
1. Go to **https://openweathermap.org/api**
2. Sign up or log in.
3. Open the menu → **My API Keys**
4. A default key is already created for you.
5. Copy the key named **Default**.
6. Paste it into the API field above.

✔ Free plan: **60 calls/minute**, no credit card needed.  
✔ This project only uses the **Current Weather Data API**.
    """)

# ---- How to get Unsplash key ----
with st.sidebar.expander("How to get a free Unsplash API Key"):
    st.markdown("""
### Steps to obtain Unsplash API Key:
1. Visit **https://unsplash.com/developers**
2. Log in or create an account.
3. Click **“New Application”**
4. Enter any name and description (example: *Weather Visualizer*).
5. Scroll to **Keys** → copy your **Access Key**.
6. Paste it into the field above.

✔ Free plan: **50 requests per hour**  
✔ “Access Key” is enough — OAuth is not required.

⚠ Required permissions:  
- **Public Access** ✓  
- **Read Photos Access** ✓  
(Do NOT enable other permissions)
    """)

# ---------------- MAIN UI -----------------
st.title("🌆 Realistic City Weather Image Generator")

city = st.text_input("City Name", "Seoul")

if st.button("Generate Image"):
    if not openweather_key or not unsplash_key:
        st.error("Please enter both API keys.")
    else:
        st.info("Fetching weather...")

        weather_type, country, temp = get_weather(city, openweather_key)

        if not weather_type:
            st.error("City not found or invalid OpenWeather key.")
        else:
            st.info(f"Weather detected: {weather_type}. Fetching image...")

            img = get_photo(city, weather_type, country, unsplash_key)

            if img is None:
                st.error("Could not fetch image. Check Unsplash API permissions.")
            else:
                poster = generate_poster(img, city, country, temp, weather_type)
                st.image(poster)

                buf = BytesIO()
                poster.save(buf, format="PNG")
                st.download_button("Download Image", buf.getvalue(), file_name="poster.png")
