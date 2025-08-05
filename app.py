import streamlit as st
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="⚾ NRFI/YRFI Model", layout="wide")

# Public Google Sheet CSV URL using gviz format (change Sheet tab name if needed)
NRFI_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/1Jhb12EMaCBwNafl0IXuaeDV2hcuo7K_Uyhb-H0U6E/gviz/tq?tqx=out:csv&sheet=NRFI"
)

st.title("⚾ NRFI/YRFI Model")
st.write("Source: Google Sheets (auto-updated)")

# -----------------------------
# Load Data Function
# -----------------------------
@st.cache_data(ttl=3600)
def load_nrfi_data():
    # Read CSV directly from Google Sheets
    df = pd.read_csv(NRFI_CSV_URL)

    # Strip whitespace from column names to avoid KeyError
    df.columns = df.columns.str.strip()

    # Ensure Confidence column exists
    if "Confidence (1-10)" not in df.columns:
        st.error("Column 'Confidence (1-10)' not found in Google Sheet.")
        st.stop()

    # Sort by Confidence column descending
    df = df.sort_values(by="Confidence (1-10)", ascending=False)

    return df

df = load_nrfi_data()

# -----------------------------
# Color Function for NRFI/YRFI
# -----------------------------
def color_predictions(val):
    if val == "NRFI":
        return "background-color: #d1f7c4; color: black;"  # Green
    elif val == "YRFI":
        return "background-color: #fcd7d7; color: black;"  # Red
    return ""

# -----------------------------
# Apply Styling
# -----------------------------
if not df.empty:
    styled_df = df.style.applymap(color_predictions, subset=["Pick"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.error("No data available in the NRFI sheet.")
