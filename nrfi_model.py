import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="NRFI Model", layout="wide")

# === BACK TO HOMEPAGE BUTTON ===
st.markdown(
    """
    <div style='text-align: left; margin-bottom: 20px;'>
        <a href="https://lineupwire.com" style="
            display: inline-block;
            padding: 8px 16px;
            background-color: black;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
        ">Back to Homepage</a>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("NRFI / YRFI Model")

# === LOAD CSV ===
CSV_FILENAME = "nrfi_model.csv"

try:
    df = pd.read_csv(CSV_FILENAME)
except FileNotFoundError:
    st.error("NRFI model CSV not found. Please run update_models.py first.")
    st.stop()

# === COLORING FUNCTION ===
def color_nrfi(val):
    if val == "NRFI":
        return "background-color: green; color: black; font-weight: bold;"
    elif val == "YRFI":
        return "background-color: red; color: black; font-weight: bold;"
    return ""

# === STYLING DATAFRAME ===
styled_df = (
    df.style
    .applymap(color_nrfi, subset=["Pick"])
    .format({"Confidence": "{:.0f}%"})  # Show confidence as whole number %
)

# === SHOW TABLE ===
st.dataframe(styled_df, use_container_width=True, hide_index=True)
