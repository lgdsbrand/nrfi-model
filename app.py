import streamlit as st
import pandas as pd
from update_models import calculate_nrfi_predictions

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

st.title("NRFI/YRFI Model")
st.markdown("[⬅️ Back to Homepage](https://lineupwire.com)")

# -----------------------------
# LOAD PREDICTIONS
# -----------------------------
try:
    df = calculate_nrfi_predictions()
except Exception as e:
    st.error(f"Error generating predictions: {e}")
    st.stop()

# Ensure DataFrame has expected columns
expected_cols = ["Game Time", "Matchup", "Pitchers", "Prediction", "Confidence %"]
for col in expected_cols:
    if col not in df.columns:
        st.error(f"Missing column in DataFrame: {col}")
        st.stop()

# Remove rows with blank Prediction (TBD pitchers)
df = df[df["Prediction"] != ""].reset_index(drop=True)

# -----------------------------
# COLOR FUNCTION FOR PREDICTION
# -----------------------------
def color_predictions(val):
    """Color NRFI as red, YRFI as green."""
    if val == "NRFI":
        return "color: red; font-weight: bold;"
    elif val == "YRFI":
        return "color: green; font-weight: bold;"
    return ""

# -----------------------------
# DISPLAY TABLE
# -----------------------------
if df.empty:
    st.warning("No valid games available today.")
else:
    styled_df = df.style.applymap(color_predictions, subset=["Prediction"])
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
