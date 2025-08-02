import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="NRFI / YRFI Model", layout="wide")
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BACK TO HOMEPAGE BUTTON ---
st.markdown("""
<div style="text-align: left; margin-bottom: 10px;">
    <a href="https://lineupwire.com" target="_self" 
       style="background-color: black; color: white; padding: 6px 16px; 
              border-radius: 12px; text-decoration: none;">
        ⬅ Back to Homepage
    </a>
</div>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown("<h1 style='display: inline;'>🔴🟢 NRFI / YRFI Model</h1>", unsafe_allow_html=True)

# --- TOGGLE BUTTONS ---
toggle = st.radio("Select View", ["Table View", "Records"], horizontal=True)

# --- LOAD DATA ---
@st.cache_data(ttl=60*60)
def load_nrfi_model():
    return pd.read_csv("nrfi_model.csv")

try:
    df = load_nrfi_model()
except FileNotFoundError:
    st.error("NRFI model data not found. Wait for next refresh.")
    st.stop()

# --- CLEAN DATA ---
if df.columns[0].lower() in ['unnamed: 0', 'index']:
    df = df.drop(df.columns[0], axis=1)

if 'Confidence' in df.columns:
    df['Confidence'] = df['Confidence'].map(lambda x: f"{int(x)}%" if pd.notnull(x) else "")

# Color only NRFI/YRFI column
def highlight_nrfi(val):
    if str(val).upper() == 'NRFI':
        return 'background-color: green; color: black; font-weight: bold;'
    elif str(val).upper() == 'YRFI':
        return 'background-color: red; color: black; font-weight: bold;'
    return ''

styled_df = df.style.applymap(highlight_nrfi, subset=['NRFI/YRFI'])

# --- AUTO RECORD TRACKING ---
record_file = "nrfi_records.csv"
today = datetime.now().date()
wins = sum(df['NRFI/YRFI'].str.upper() == "NRFI")
losses = sum(df['NRFI/YRFI'].str.upper() == "YRFI")
today_record = pd.DataFrame([[today, "NRFI Model", wins, losses,
                              f"{(wins/(wins+losses))*100:.0f}%"]],
                              columns=["Date","Model","Wins","Losses","Win%"])
try:
    old_records = pd.read_csv(record_file)
except:
    old_records = pd.DataFrame(columns=today_record.columns)
if str(today) not in old_records["Date"].astype(str).values:
    pd.concat([old_records, today_record], ignore_index=True).to_csv(record_file, index=False)

# --- TOGGLE VIEWS ---
if toggle == "Table View":
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

elif toggle == "Records":
    try:
        rec = pd.read_csv(record_file)
        rec['Date'] = pd.to_datetime(rec['Date'])
        rec['Week'] = rec['Date'].dt.isocalendar().week
        rec['Month'] = rec['Date'].dt.month
        st.subheader("Daily Records")
        st.dataframe(rec.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        st.subheader("Weekly Summary")
        st.dataframe(rec.groupby("Week")[["Wins","Losses"]].sum(), use_container_width=True)
        st.subheader("Monthly Summary")
        st.dataframe(rec.groupby("Month")[["Wins","Losses"]].sum(), use_container_width=True)
    except FileNotFoundError:
        st.info("No record file yet.")
