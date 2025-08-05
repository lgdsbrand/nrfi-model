import streamlit as st
import pandas as pd

st.set_page_config(page_title="⚾ NRFI/YRFI Model", layout="wide")

st.title("⚾ NRFI/YRFI Model")
st.write("Source: Google Sheets (auto-updated)")

# -----------------------------
# CONFIG
# -----------------------------
# Replace with your actual NRFI tab CSV link
NRFI_CSV_URL = "https://docs.google.com/spreadsheets/d/1Jhb12EMaCBwNafl0IXuaeDV2hcuo7K_Uyhb-H0U6E/export?format=csv&gid=NRFI"

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    df = pd.read_csv(NRFI_CSV_URL)
except Exception as e:
    st.error(f"Failed to load NRFI data: {e}")
    st.stop()

# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Check for empty table
if df.empty:
    st.error("No data found in the NRFI Google Sheet.")
    st.stop()

# Sort by confidence if column exists
if "Confidence (1-10)" in df.columns:
    df = df.sort_values(by="Confidence (1-10)", ascending=False)

# Display table (just like MLB model first)
st.dataframe(df, use_container_width=True, hide_index=True)
