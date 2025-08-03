import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------------------
# BACK TO HOMEPAGE BUTTON
# ---------------------------
st.markdown(
    """
    <a href="https://lineupwire.com" style="
        display:inline-block;
        padding:6px 12px;
        background-color:black;
        color:white;
        border-radius:6px;
        text-decoration:none;
        font-weight:bold;
        margin-bottom:12px;
    ">
    ⬅ Back to Homepage
    </a>
    """,
    unsafe_allow_html=True
)

st.title("🔴🟢 MLB NRFI / YRFI Model")

# ---------------------------
# LOAD MODEL DATA
# ---------------------------
CSV_FILE = "nrfi_model.csv"

try:
    df = pd.read_csv(CSV_FILE)

    # Ensure NRFI/YRFI column exists
    if "Pick" not in df.columns:
        st.error("NRFI model data is missing the 'Pick' column.")
    else:
        # Color the NRFI/YRFI cells
        def color_nrfi(val):
            if val == "NRFI":
                return "background-color: green; color: black"
            elif val == "YRFI":
                return "background-color: red; color: black"
            return ""

        # Hide index, apply color
        st.dataframe(
            df.style.applymap(color_nrfi, subset=["Pick"]),
            use_container_width=True
        )

except FileNotFoundError:
    st.error("NRFI model data not found. Wait for the next refresh to generate today's CSV.")
