import streamlit as st
import pandas as pd
from update_models import get_today_games, calculate_nrfi

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Title and Back to Homepage
st.markdown("## NRFI/YRFI Model")
st.markdown("⬅️ [Back to Homepage](https://lineupwire.com)")

# -----------------------------
# Load Data and Run Model
# -----------------------------
st.write("Fetching today's MLB games and calculating NRFI/YRFI confidence...")

games_df = get_today_games()

if games_df.empty:
    st.warning("No MLB games found for today. Check the ESPN API or try again later.")
else:
    results_df = calculate_nrfi(games_df)

    # Color NRFI green and YRFI red
    def color_predictions(val):
        if val == "NRFI":
            return "color: green; font-weight: bold"
        elif val == "YRFI":
            return "color: red; font-weight: bold"
        return ""

    # Format confidence percentage
    if "Confidence %" in results_df.columns:
        results_df["Confidence %"] = results_df["Confidence %"].apply(lambda x: f"{x}%" if x != "" else "")

    # Display table without index
    st.dataframe(
        results_df.style.applymap(color_predictions, subset=["Prediction"]),
        use_container_width=True,
        hide_index=True
    )
