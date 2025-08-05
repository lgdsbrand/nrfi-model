import streamlit as st
import pandas as pd

st.set_page_config(page_title="⚾ NRFI/YRFI Model", layout="wide")
st.title("⚾ NRFI/YRFI Model")
st.write("Source: Google Sheets (auto-updated)")

NRFI_CSV_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/gviz/tq?tqx=out:csv&sheet=NRFI"

@st.cache_data(ttl=3600)
def load_nrfi_data():
    df = pd.read_csv(NRFI_CSV_URL)
    df = df.sort_values(by="Confidence (1-10)", ascending=False)
    return df

df = load_nrfi_data()

# Display the table with only the 5 columns from the Google Sheet
st.dataframe(
    df[['Game','Pitchers','Model %','NRFI/YRFI','Confidence (1-10)']],
    use_container_width=True,
    hide_index=True
)
