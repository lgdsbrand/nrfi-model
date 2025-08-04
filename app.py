import streamlit as st
import pandas as pd

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Title and Back to Homepage
st.markdown("## NRFI/YRFI Model")
st.markdown("⬅️ [Back to Homepage](https://lineupwire.com)")

# -----------------------------
# Load Model Output
# -----------------------------
try:
    df = pd.read_csv("nrfi_model.csv")
except FileNotFoundError:
    st.error("No NRFI model file found. Please wait for the GitHub Action to generate it.")
    st.stop()

if df.empty:
    st.warning("No games found for today.")
else:
    # Format confidence as percentage string if numeric
    if "Confidence %" in df.columns:
        df["Confidence %"] = df["Confidence %"].apply(
            lambda x: f"{x}%" if x != "" and not pd.isna(x) else ""
        )

    # -----------------------------
    # Color NRFI red, YRFI green
    # -----------------------------
    def color_predictions(val):
        if val == "NRFI":
            return "background-color: red; color: white; font-weight: bold"
        elif val == "YRFI":
            return "background-color: green; color: white; font-weight: bold"
        return ""

    # Display without index
    st.dataframe(
        df.style.applymap(color_predictions, subset=["Prediction"]),
        use_container_width=True,
        hide_index=True
    )
