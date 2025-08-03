import streamlit as st
import pandas as pd
from update_models import get_today_games, calculate_nrfi

st.set_page_config(page_title="NRFI / YRFI Model", layout="wide")
st.title("⚾ MLB NRFI / YRFI Confidence Model")

st.write(
    """
    This model automatically:
    - Scrapes today's MLB games and starting pitchers
    - Calculates NRFI % based on team & pitcher first-inning stats
    - Classifies games as **NRFI (≥60%)** or **YRFI (<60%)**
    - Sorts by highest confidence first
    """
)

# Fetch today's games and calculate model predictions
games_df = get_today_games()
final_df = calculate_nrfi(games_df)

# Format confidence with % sign
final_df["Confidence %"] = final_df["Confidence %"].astype(str) + "%"

# Display the final predictions in a clean table
st.dataframe(final_df.style.hide(axis="index"), use_container_width=True)

# Optional: allow CSV download of today's predictions
csv = final_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Predictions as CSV",
    data=csv,
    file_name="nrfi_predictions.csv",
    mime="text/csv",
)
