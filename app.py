import streamlit as st
import pandas as pd
from update_models import calculate_nrfi_predictions

st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

st.title("NRFI/YRFI Model")
st.markdown("⬅️ [Back to Homepage](https://lineupwire.com)")

# Load predictions
df = calculate_nrfi_predictions()

# Color NRFI/YRFI
def color_prediction(val):
    if val == "NRFI":
        return "color: red; font-weight: bold;"
    elif val == "YRFI":
        return "color: green; font-weight: bold;"
    return ""

# Display styled table
st.dataframe(
    df.style.applymap(color_prediction, subset=["Prediction"]),
    use_container_width=True,
    hide_index=True
)
