import streamlit as st
from update_models import get_today_games, calculate_nrfi

st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Top layout
col1, col2 = st.columns([4, 1])
with col1:
    st.title("⚾ NRFI / YRFI Model")
with col2:
    st.markdown("[🏠 Back to Homepage](https://lgdsbrand.streamlit.app)")

# Get data
games_df = get_today_games()
final_df = calculate_nrfi(games_df)

# Add Confidence formatting
final_df["Confidence %"] = final_df["Confidence %"].astype(str) + "%"

# Color styling
def highlight_prediction(val):
    if val == "NRFI":
        return "background-color: lightgreen; color: black;"
    else:
        return "background-color: lightcoral; color: black;"

styled_df = final_df.style.applymap(highlight_prediction, subset=["Prediction"]).hide(axis="index")

st.dataframe(styled_df, use_container_width=True)
