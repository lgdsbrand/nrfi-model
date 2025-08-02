import streamlit as st
import pandas as pd

st.set_page_config(page_title="NRFI / YRFI Model", page_icon="⚾", layout="centered")

# Hide Streamlit menu & footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Back to homepage button
st.markdown(
    """
    <a href="https://lineupwire.com" target="_self">
        <button style="
            background-color: black; 
            color: white; 
            border-radius: 10px; 
            padding: 6px 12px;
            border: none;
            margin-bottom: 15px;">
        ⬅ Back to Homepage
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

st.markdown("## 🔴🟢 NRFI / YRFI Model")

# Load NRFI CSV
try:
    df = pd.read_csv("nrfi_model.csv")

    # Color cells based on Pick column only
    def color_cells(val):
        if val == "NRFI":
            return "background-color: red; color: black;"
        elif val == "YRFI":
            return "background-color: green; color: black;"
        return ""

    st.dataframe(df.style.applymap(color_cells, subset=["Pick"]), use_container_width=True)

except FileNotFoundError:
    st.error("NRFI model data not found. Wait for next refresh.")
