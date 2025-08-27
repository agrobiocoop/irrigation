import streamlit as st
import requests
import pandas as pd
import math
from datetime import date

st.title("Υπολογιστής Άρδευσης Αβοκάντο 🌱💧")

# --- Επιλογή τύπου εισόδου ETo ---
input_type = st.radio("Πηγή δεδομένων εξατμισοδιαπνοής (ETo):",
                      ("Open-Meteo", "Δική μου τιμή"))

if input_type == "Δική μου τιμή":
    eto = st.number_input("Βάλε ETo (mm/ημέρα):", min_value=0.0, value=5.0, step=0.1)
else:
    # Λήψη Open-Meteo
    lat = st.number_input("Latitude:", value=35.4239)
    lon = st.number_input("Longitude:", value=23.9237)
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": lat, "longitude": lon,
                  "daily": "evapotranspiration", "timezone": "auto"}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "daily" in data and "evapotranspiration" in data["daily"]:
            eto = data["daily"]["evapotranspiration"][0]
            st.info(f"Λήφθηκε ETo: {eto:.2f} mm/ημέρα")
        else:
            st.warning("Δεν βρέθηκαν δεδομένα ETo, χρησιμοποιείται default 5 mm")
            eto = 5
    except Exception as e:
        st.error(f"Σφάλμα Open-Meteo: {e}. Χρησιμοποιείται default 5 mm")
        eto = 5

# --- Inputs χρήστη ---
age = st.selectbox("Ηλικία δέντρου (έτη):", [1, 2, 3, 5, 10])
soil = st.selectbox("Τύπος εδάφους:", ["Αμμώδες", "Αμμοπηλώδες", "Πηλώδες"])
canopy_diameter = st.number_input("Διάμετρος κόμης (m):", min_value=0.2, max_value=12.0, value=1.0, step=0.1)

# --- Συντελεστές ---
KC_BY_AGE = {1: 0.55, 2: 0.60, 3: 0.65, 5: 0.75, 10: 0.90}
SOIL_FACTORS = {"Αμμώδες": 1.2, "Αμμοπηλώδες": 1.0, "Πηλώδες": 0.8}

# --- Υπολογισμός ---
kc = KC_BY_AGE.get(age, 0.8)
soil_factor = SOIL_FACTORS.get(soil, 1.0)
area = math.pi * (canopy_diameter / 2) ** 2  # m²

water_liters = eto * kc * area * soil_factor  # liters/day per tree

# --- Εμφάνιση αποτελέσματος ---
st.subheader("💧 Αποτελέσματα")
st.write(f"Ηλικία δέντρου: {age} έτη")
st.write(f"Διάμετρος κόμης: {canopy_diameter:.2f} m")
st.write(f"Τύπος εδάφους: {soil}")
st.write(f"Ημερήσια ανάγκη νερού: **{water_liters:.2f} λίτρα/δέντρο**")

# --- Αποθήκευση σε CSV ---
if st.button("Αποθήκευση δεδομένων"):
    today = date.today().isoformat()
    data = {
        "date": [today],
        "age": [age],
        "soil": [soil],
        "canopy_diameter_m": [canopy_diameter],
        "eto_mm": [eto],
        "kc": [kc],
        "soil_factor": [soil_factor],
        "water_liters_per_tree": [water_liters]
    }
    df = pd.DataFrame(data)
    try:
        df.to_csv("irrigation_log.csv", mode="a", index=False, header=not pd.io.common.file_exists("irrigation_log.csv"))
        st.success("✅ Τα δεδομένα αποθηκεύτηκαν στο irrigation_log.csv")
    except Exception as e:
        st.error(f"Σφάλμα κατά την αποθήκευση: {e}")
