# trigger rebuild

import streamlit as st
import pandas as pd
import importlib
import update_models

# Force reload to avoid import cache issues
importlib.reload(update_models)
from update_models import get_today_games, calculate_nrfi

# Configure page
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Title + Back Button
col1, col2 = st.columns([3,1])
with col1:
    st.title("NRFI/YRFI Model")
with col2:
    st.markdown("[⬅ Back to Homepage](https://lineupwire.com)")

# Get games and calculate NRFI
games = get_today_games()
df = calculate_nrfi(games)

# Color-code predictions
def highlight_predictions(val):
    if val == "NRFI":
        return "background-color: red; color: white;"
    else:
        return "background-color: green; color: white;"

styled_df = df.style.applymap(highlight_predictions, subset=["Prediction"])

# Display without index
st.dataframe(styled_df, use_container_width=True, hide_index=True)
