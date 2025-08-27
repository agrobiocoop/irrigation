import streamlit as st
import requests
import pandas as pd
from datetime import date

# Συντελεστές κατανάλωσης νερού ανά ηλικία (m³/ημέρα)
AGE_WATER_FACTORS = {
    1: 5,
    2: 10,
    3: 20,
    5: 40,
    10: 70
}

# Συντελεστές ανά τύπο εδάφους
SOIL_FACTORS = {
    "Αμμώδες": 1.2,
    "Αμμοπηλώδες": 1.0,
    "Πηλώδες": 0.8
}

# Συντεταγμένες Βατόλακος Χανίων
LAT, LON = 35.46, 23.95

st.title("🌱 Υπολογισμός Άρδευσης Αβοκάντο")

# Είσοδοι χρήστη
age = st.selectbox("Ηλικία δέντρου (έτη):", [1, 2, 3, 5, 10])
soil = st.selectbox("Τύπος εδάφους:", list(SOIL_FACTORS.keys()))

# Φέρνουμε meteo δεδομένα
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,precipitation_sum&timezone=auto"
response = requests.get(url).json()

today = date.today().isoformat()
try:
    tmax = response["daily"]["temperature_2m_max"][0]
    rain = response["daily"]["precipitation_sum"][0]
except Exception:
    tmax, rain = 25, 0  # default values αν δεν έχει δεδομένα

# Υπολογισμός άρδευσης
base_need = AGE_WATER_FACTORS[age]
soil_factor = SOIL_FACTORS[soil]

water_need = base_need * soil_factor

# Αφαιρούμε βροχόπτωση (mm -> λίτρα/m² -> m³/δέντρο περίπου)
# απλουστευμένη παραδοχή: 1 mm = 1 λίτρο/m²
effective_rain = max(0, rain * 0.5)  # 50% απορροφησιμότητα
water_need = max(0, water_need - effective_rain)

st.subheader("💧 Αποτελέσματα")
st.write(f"Ημερήσια ανάγκη: **{water_need:.2f} m³/δέντρο**")
st.write(f"(Tmax: {tmax}°C, Βροχή: {rain} mm)")

# Αποθήκευση σε αρχείο CSV
data = {
    "date": [today],
    "age": [age],
    "soil": [soil],
    "tmax": [tmax],
    "rain": [rain],
    "water_need_m3": [water_need]
}
df = pd.DataFrame(data)
df.to_csv("irrigation_log.csv", mode="a", header=False, index=False)

st.success("✅ Τα δεδομένα αποθηκεύτηκαν στο irrigation_log.csv")
