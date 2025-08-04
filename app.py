import streamlit as st
import pandas as pd
from update_models import get_today_games, calculate_nrfi

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Title and Back Button
st.title("NRFI/YRFI Model")
st.markdown("⬅️ [Back to Homepage](https://lineupwire.com)")  # Update to your actual homepage

# -----------------------------
# LOAD DATA
# -----------------------------
df = get_today_games()
df = calculate_nrfi(df)

# -----------------------------
# Apply Prediction Logic
# -----------------------------
# Mark TBD games as blank
df.loc[df['Pitchers'].str.contains("TBD", case=False, na=False), ['Prediction', 'Confidence %']] = ""

# -----------------------------
# Style Function for Prediction Column
# -----------------------------
def color_prediction(val):
    if val == "NRFI":
        return "color: red; font-weight: bold;"
    elif val == "YRFI":
        return "color: green; font-weight: bold;"
    return ""

# -----------------------------
# Display Styled Table
# -----------------------------
# Hide index and style Prediction column
styled_df = df.style.applymap(color_prediction, subset=["Prediction"])

# Use st.table for styled DataFrame
st.table(styled_df)
