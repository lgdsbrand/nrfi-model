import streamlit as st
import pandas as pd
from update_models import get_today_games, calculate_nrfi

st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Title & Back Button
st.markdown("<h1 style='display:flex; justify-content:space-between;'>NRFI/YRFI Model</h1>", unsafe_allow_html=True)
st.markdown("⬅️ [Back to Homepage](https://lineupwire.com)")

# Fetch and display games
games_df = get_today_games()

if not games_df.empty:
    results_df = calculate_nrfi(games_df)
    
    # Highlight NRFI Green, YRFI Red
    def highlight_prediction(val):
        color = "green" if val == "NRFI" else "red"
        return f"color: {color}; font-weight: bold"

    st.dataframe(results_df.style.applymap(highlight_prediction, subset=["Prediction"]), use_container_width=True)
else:
    st.warning("No MLB games found for today.")
