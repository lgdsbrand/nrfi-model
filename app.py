import streamlit as st
import pandas as pd
from update_models import get_today_games, calculate_nrfi

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# ---------------------------
# TITLE + BACK TO HOMEPAGE
# ---------------------------
col1, col2 = st.columns([4, 1])
with col1:
    st.title("NRFI/YRFI MODEL")
with col2:
    st.markdown(
        "<a href='https://lineupwire.com' style='text-decoration:none;'>"
        "<button style='font-size:16px;padding:6px 12px;margin-top:10px;'>Back to Homepage</button>"
        "</a>",
        unsafe_allow_html=True
    )

st.write(" ")  # Spacer

# ---------------------------
# LOAD AND DISPLAY MODEL RESULTS
# ---------------------------
st.subheader("Today's Games with NRFI/YRFI Predictions")

# Calculate predictions
try:
    df = calculate_nrfi()

    # Color NRFI/YRFI cells
    def highlight_prediction(val):
        color = 'green' if val == "NRFI" else 'red'
        return f'color: {color}; font-weight: bold'

    styled_df = df.style.applymap(highlight_prediction, subset=["Prediction"])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error loading NRFI model: {e}")
