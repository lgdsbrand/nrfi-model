import streamlit as st
from nrfi_model import run_nrfi_app

# Set page config
st.set_page_config(page_title="LineupWire NRFI Model", layout="wide")

# Run NRFI Model directly
run_nrfi_app()
