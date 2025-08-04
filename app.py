import streamlit as st
import pandas as pd

# Replace this with your Google Sheet CSV URL
NRFI_CSV_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=NRFI_MODEL_GID"

st.title("⚾ NRFI/YRFI Model")

@st.cache_data(ttl=3600)
def load_nrfi_data():
    df = pd.read_csv(NRFI_CSV_URL)
    # Sort by confidence descending
    df = df.sort_values(by="Confidence (1-10)", ascending=False)
    return df

df = load_nrfi_data()

# Color function
def color_predictions(val):
    if val == "NRFI":
        return "background-color: #fcd7d7; color: black;"  # Red
    elif val == "YRFI":
        return "background-color: #d1f7c4; color: black;"  # Green
    return ""

# Apply color styling only to NRFI/YRFI column
styled_df = df.style.applymap(color_predictions, subset=["NRFI/YRFI"])

st.dataframe(styled_df, use_container_width=True, hide_index=True)
