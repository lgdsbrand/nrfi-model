import streamlit as st
from update_models import run_nrfi_model

st.set_page_config(page_title="NRFI Model", layout="wide")
st.title("⚾ MLB NRFI Model - Real Stats")

st.write("Daily automated NRFI % based on team/pitcher 1st inning stats and weather factors.")

df = run_nrfi_model()
st.dataframe(df.style.hide(axis="index"), use_container_width=True)
