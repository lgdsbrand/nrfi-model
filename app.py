import streamlit as st
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="⚾ NRFI/YRFI Model", layout="wide")

# Your Google Sheet CSV URL
NRFI_CSV_URL = "https://docs.google.com/spreadsheets/d/1Jhb12EM_hac0mValF0lXlue0V2hcuo7K_Uyhb-H0U6E/gviz/tq?tqx=out:csv&sheet=NRFI"

st.title("⚾ NRFI/YRFI Model")
st.write("Source: Google Sheets (auto-updated)")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=3600)
def load_nrfi_data():
    df = pd.read_csv(NRFI_CSV_URL)

    # Strip spaces from column names to avoid KeyErrors
    df.rename(columns=lambda x: x.strip(), inplace=True)

    # Print columns for debugging
    st.write("Columns found:", df.columns.tolist())

    # Ensure required columns exist
    if "Confidence (1-10)" not in df.columns or "Pick" not in df.columns:
        st.error("Google Sheet is missing required columns: 'Pick' or 'Confidence(1-10)'")
        st.stop()

    # Sort by Confidence descending
    df = df.sort_values(by="Confidence (1-10)", ascending=False)
    return df

df = load_nrfi_data()

if df.empty:
    st.error("No data found in Google Sheet.")
    st.stop()

# -----------------------------
# COLOR FUNCTION
# -----------------------------
def color_predictions(val):
    if val == "NRFI":
        return "background-color: #d1f7c4; color: black;"  # Green
    elif val == "YRFI":
        return "background-color: #fcd7d7; color: black;"  # Red
    return ""

# Apply color styling only to Pick column
styled_df = df.style.applymap(color_predictions, subset=["Pick"])

# -----------------------------
# DISPLAY TABLE
# -----------------------------
st.dataframe(styled_df, use_container_width=True, hide_index=True)
