import streamlit as st
import pandas as pd
from update_models import calculate_nrfi_predictions

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

st.title("NRFI/YRFI Model")
st.markdown("[⬅️ Back to Homepage](https://lineupwire.com)")

# -----------------------------
# GET PREDICTIONS
# -----------------------------
df = calculate_nrfi_predictions()

# Filter out games with TBD pitchers
if 'Pitchers' in df.columns:
    df['Skip'] = df['Pitchers'].apply(lambda x: 'TBD' in x if isinstance(x, str) else False)
    df.loc[df['Skip'], ['Prediction', 'Confidence %']] = ""
    df.drop(columns=['Skip'], inplace=True)

# -----------------------------
# COLOR FUNCTION
# -----------------------------
def color_predictions(val):
    """Color NRFI as red, YRFI as green."""
    if val == "NRFI":
        return "color: red; font-weight: bold;"
    elif val == "YRFI":
        return "color: green; font-weight: bold;"
    return ""

# -----------------------------
# SHOW DATAFRAME
# -----------------------------
if df.empty:
    st.warning("No games available today.")
else:
    styled_df = df.style.applymap(color_predictions, subset=["Prediction"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
