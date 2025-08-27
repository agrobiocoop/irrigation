import streamlit as st
import requests
import math

# Συντελεστές Kc ανά ηλικία (προσεγγιστικά)
KC_BY_AGE = {
    1: 0.55,
    2: 0.60,
    3: 0.65,
    5: 0.75,
    10: 0.90
}

# Υπολογισμός άρδευσης
def calculate_irrigation(eto_mm, age, canopy_diameter):
    kc = KC_BY_AGE.get(age, 0.8)
    area = math.pi * (canopy_diameter / 2) ** 2  # m²
    liters_per_day = eto_mm * kc * area
    return liters_per_day

# Λήψη δεδομένων ETo από Open-Meteo
def get_eto(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "evapotranspiration",
        "timezone": "auto"
    }
    r = requests.get(url, params=params)
    data = r.json()
    eto_today = data["daily"]["evapotranspiration"][0]  # mm/day
    return eto_today

# Streamlit UI
st.title("Υπολογιστής Άρδευσης Αβοκάντο 🌱💧")

age = st.selectbox("Ηλικία δέντρου (έτη):", [1, 2, 3, 5, 10])
canopy_diameter = st.number_input("Διάμετρος κόμης (m):", min_value=0.2, max_value=12.0, value=1.0, step=0.1)

if st.button("Υπολόγισε"):
    eto = get_eto(35.4239, 23.9237)  # Βατόλακκος Χανίων
    water_liters = calculate_irrigation(eto, age, canopy_diameter)
    st.success(f"Το δέντρο ηλικίας {age} ετών χρειάζεται περίπου {water_liters:.1f} λίτρα/ημέρα 💧")
