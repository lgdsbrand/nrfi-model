import streamlit as st
from update_models import run_nrfi_model

st.set_page_config(page_title="NRFI Model", layout="wide")
st.title("⚾ MLB NRFI Model")

st.write("Automatically scrapes today's games and calculates NRFI confidence %")

# Run the NRFI model
df = run_nrfi_model()

# Display table sorted by highest NRFI %
st.dataframe(df, use_container_width=True)
