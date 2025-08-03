import streamlit as st
import pandas as pd
from update_models import run_nrfi_model

st.set_page_config(page_title="NRFI Model", layout="wide")
st.title("MLB NRFI / YRFI Model")

st.write("Daily NRFI model with TheCrowdsLine.ai data.")

df = run_nrfi_model()

# Apply color styling for NRFI (green) and YRFI (red)
def highlight_pick(val):
    if val == "NRFI":
        return "background-color: lightgreen; color: black"
    elif val == "YRFI":
        return "background-color: lightcoral; color: black"
    return ""

st.dataframe(df.style.applymap(highlight_pick, subset=["Pick"]))
