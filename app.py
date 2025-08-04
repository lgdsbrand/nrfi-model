import streamlit as st
import pandas as pd
from update_models import calculate_nrfi_predictions

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# -----------------------------
# HEADER & BACK BUTTON
# -----------------------------
st.markdown("# NRFI/YRFI Model")
st.markdown("⬅️ [Back to Homepage](https://lineupwire.com)", unsafe_allow_html=True)

# -----------------------------
# LOAD PREDICTIONS
# -----------------------------
df = calculate_nrfi_predictions()

# Drop any rows where Prediction is blank
df = df[df["Prediction"] != ""]

# Reorder / select columns for display
df_display = df[[
    "Time",
    "Matchup",
    "Pitchers",
    "Prediction",
    "Confidence %"
]].reset_index(drop=True)

# -----------------------------
# COLOR FUNCTION
# -----------------------------
def color_prediction(val):
    if val == "NRFI":
        return "color: red; font-weight: bold;"
    elif val == "YRFI":
        return "color: green; font-weight: bold;"
    return ""

# -----------------------------
# STYLE AND DISPLAY TABLE
# -----------------------------
st.dataframe(
    df_display.style.applymap(color_prediction, subset=["Prediction"]),
    use_container_width=True,
    hide_index=True
)
