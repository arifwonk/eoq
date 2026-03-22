import streamlit as st
import pandas as pd
import numpy as np
import io
import bcrypt
from supabase import create_client

# Connection
SUPABASE_URL = "https://glxjsgzismusmhzwvfud.supabase.co"
SUPABASE_KEY = "sb_publishable_kKw9D8hXE-gsEWXp1cJxQQ_U6RZEF-A"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# FUNCTION LOGIN
st.title("📦 Inventory Analysis (ROP, EOQ, Safety Stock)")


def check_login(username, password):

    response = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .eq("password", password) \
        .execute()

    if len(response.data) > 0:
        return True
    return False

# UI LOGIN


def login():
    st.title("🔐 Login ")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state["login"] = True
            st.session_state["user"] = username
        else:
            st.error("Login gagal")


# cek login (PROTECT APP)
if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    login()
    st.stop()

# Upload file
uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])


def get_z(service_level):
    if service_level >= 0.99:
        return 2.33
    elif service_level >= 0.98:
        return 2.05
    elif service_level >= 0.97:
        return 1.88
    elif service_level >= 0.95:
        return 1.65
    elif service_level >= 0.90:
        return 1.28
    else:
        return 1.65


if uploaded_file:

    df = pd.read_excel(uploaded_file, header=1)

    hasil = []

    for kode, group in df.groupby("Kode_Barang"):

        demand = group["Pemakaian"]

        avg = demand.mean()
        std = demand.std(ddof=1)
        max_demand = demand.max()

        lead_time = group["Lead_Time"].iloc[0]
        service_level = group["Service_Level"].iloc[0]
        biaya_pesan = group["Biaya_Pesan"].iloc[0]
        biaya_simpan = group["Biaya_Simpan"].iloc[0]

        z = get_z(service_level)

        # Perhitungan
        safety_stock = z * std * np.sqrt(lead_time)
        rop = (avg * lead_time) + safety_stock
        max_stock = rop + (avg * lead_time)

        demand_1year = avg * 365
        eoq = np.sqrt((2 * demand_1year * biaya_pesan) / biaya_simpan)

        # Simulasi current stock
        current_stock = group["Current_Stock"].iloc[0]

        status = "ORDER" if current_stock <= rop else "SAFE"
        doi = int(np.ceil(current_stock / avg)) if avg != 0 else 0

        hasil.append({
            "Kode_Barang": kode,
            "Service_Level": service_level,
            "Lead_Time": lead_time,
            "Average": round(avg, 2),
            "Safety_Stock": int(np.ceil(safety_stock)),
            "ROP": int(np.ceil(rop)),
            "EOQ": int(np.ceil(eoq)),
            "Current_Stock": current_stock,
            "DOI": doi,
            "Status": status
        })

    df_hasil = pd.DataFrame(hasil)

    st.subheader("📊 Hasil Perhitungan")
    st.dataframe(df_hasil)

    buffer = io.BytesIO()
    df_hasil.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="⬇️ Download Excel",
        data=buffer,
        file_name="hasil.xlsx"
    )

# =========================
# LOGOUT
# =========================
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()
