import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Weather → Visual Style Mapping
# -----------------------------
def get_weather_style(condition):
    condition = condition.lower()
    if "rain" in condition:
        return {
            "bg_color": (40, 40, 60),
            "accent": (120, 120, 255),
            "icon": "🌧️"
        }
    elif "cloud" in condition:
        return {
            "bg_color": (60, 60, 60),
            "accent": (200, 200, 200),
            "icon": "☁️"
        }
    elif "clear" in condition:
        return {
            "bg_color": (255, 200, 80),
            "accent": (255, 255, 255),
            "icon": "☀️"
        }
    elif "snow" in condition:
        return {
            "bg_color": (230, 240, 255),
            "accent": (120, 160, 255),
            "icon": "❄️"
        }
    else:
        return {
            "bg_color": (80, 80, 80),
            "accent": (255, 255, 255),
            "icon": "🌈"
        }

# -----------------------------
# Generate Poster (PIL)
# -----------------------------
def generate_poster(city, temp, condition, width, height):
    style = get_weather_style(condition)

    # Create Canvas
    img = Image.new("RGB", (width, height), style["bg_color"])
    draw = ImageDraw.Draw(img)

    # Load Default Font
    font_title = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # Draw Title
    title_text = f"{style['icon']} {condition.capitalize()}"
    draw.text((width//2 - 80, 40), title_text, fill=style["accent"], font=font_title)

    # Temperature (large)
    draw.text((width//2 - 40, height//2 - 20), f"{temp}°C",
              fill=style["accent"], font=font_title)

    # City label
    draw.text((20, height - 40), f"{city}", fill="white", font=font_small)

    # Weather Info
    draw.text((20, height - 20), f"{condition.capitalize()}", fill="white", font=font_small)

    return img

# -----------------------------
# PIL → Bytes
# -----------------------------
def poster_to_bytes(poster):
    buffer = BytesIO()
    poster.save(buffer, format="PNG")
    return buffer.getvalue()


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Weather Poster Generator", layout="centered")

st.title("🌤️ Weather-Based Generative Poster")

st.sidebar.header("Configuration")

api_key = st.sidebar.text_input("Enter your OpenWeather API Key:", type="password")
city = st.sidebar.text_input("City Name", "Guangdong")

width = st.sidebar.slider("Poster Width", 400, 1200, 600)
height = st.sidebar.slider("Poster Height", 400, 1600, 800)

if st.sidebar.button("Generate Poster"):
    if not api_key:
        st.error("Please enter your API key.")
    else:
        # Request Weather Data
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            st.error("❌ API request failed. Please check your city name or API key.")
        else:
            data = response.json()
            temp = data["main"]["temp"]
            condition = data["weather"][0]["description"]

            poster = generate_poster(city, temp, condition, width, height)
            byte_data = poster_to_bytes(poster)

            st.image(byte_data, caption=f"{city} | {temp}°C | {condition}")

            # Provide Download Button
            st.download_button(
                label="Download Poster",
                data=byte_data,
                file_name=f"{city}_weather_poster.png",
                mime="image/png"
            )
