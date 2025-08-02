import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Hide GitHub and menu items
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Title
st.markdown(
    "<h1 style='text-align: center;'>🔴🟢 NRFI / YRFI Model</h1>",
    unsafe_allow_html=True
)

csv_file = "nrfi_model.csv"

# Load CSV safely
if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
    st.error("NRFI model data not found. Wait for next refresh.")
else:
    df = pd.read_csv(csv_file)

    # Ensure correct column names
    expected_cols = ["Game Time", "Away Team", "Home Team", "Pick", "Confidence"]
    if list(df.columns) != expected_cols:
        st.error(f"CSV format mismatch. Expected columns: {expected_cols}")
    else:
        # Color cells: NRFI = green, YRFI = red
        def color_pick(val):
            if val == "NRFI":
                return "background-color: green; color: black;"
            elif val == "YRFI":
                return "background-color: red; color: black;"
            return ""

        # Apply styling
        styled_df = df.style.applymap(color_pick, subset=["Pick"])
        st.dataframe(styled_df, use_container_width=True)
