import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="NRFI / YRFI Model", layout="wide")
hide_streamlit_style = """
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- BACK TO HOMEPAGE BUTTON ---
st.markdown("""
<div style="text-align: left;">
    <a href="https://lineupwire.com" target="_self" 
       style="background-color: black; color: white; padding: 6px 16px; 
              border-radius: 12px; text-decoration: none;">
        ⬅ Back to Homepage
    </a>
</div>
""", unsafe_allow_html=True)

# --- TITLE ON ONE LINE ---
st.markdown("<h1 style='display: inline;'>🔴🟢 NRFI / YRFI Model</h1>", unsafe_allow_html=True)

# --- LOAD DATA ---
try:
    df = pd.read_csv("nrfi_model.csv")  # Make sure this file exists
except FileNotFoundError:
    st.error("Error loading NRFI Model: nrfi_model.csv not found")
    st.stop()

# --- CLEAN DATA ---
if df.columns[0].lower() in ['unnamed: 0', 'index']:
    df = df.drop(df.columns[0], axis=1)

# Ensure Confidence is integer %
if 'Confidence' in df.columns:
    df['Confidence'] = df['Confidence'].map(lambda x: f"{int(x)}%" if pd.notnull(x) else "")

# Color only NRFI/YRFI column
def highlight_nrfi(val):
    if val.upper() == 'NRFI':
        return 'background-color: red; color: black; font-weight: bold;'
    elif val.upper() == 'YRFI':
        return 'background-color: green; color: black; font-weight: bold;'
    return ''

styled_df = df.style.applymap(highlight_nrfi, subset=['NRFI/YRFI'])

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)
