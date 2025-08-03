import streamlit as st
from update_models import get_today_games, calculate_nrfi

st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Top buttons
col1, col2 = st.columns([4,1])
with col1:
    st.title("⚾ NRFI / YRFI Model")
with col2:
    st.markdown("[🏠 Back to Homepage](https://lgdsbrand.streamlit.app)")

games_df = get_today_games()
final_df = calculate_nrfi(games_df)

# Hide index, format Confidence
final_df["Confidence %"] = final_df["Confidence %"].astype(str) + "%"
st.dataframe(final_df.style.hide(axis="index"), use_container_width=True)
