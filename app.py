import streamlit as st
import pandas as pd
from update_models import get_today_games, calculate_nrfi

st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# ---- Title & Back Button ----
col1, col2 = st.columns([3, 1])
with col1:
    st.title("NRFI / YRFI Model")
with col2:
    if st.button("⬅ Back to Homepage"):
        st.write("Return to your main site URL here...")  # Replace with actual homepage link

# ---- Get Today's Games & Calculate NRFI/YRFI ----
try:
    df = calculate_nrfi(get_today_games())
except Exception as e:
    st.error(f"Error calculating NRFI/YRFI: {e}")
    st.stop()

# ---- Determine NRFI/YRFI Outcome & Confidence ----
def classify_result(row):
    if row["NRFI %"] >= 60:  # 60%+ = NRFI
        return "NRFI"
    else:
        return "YRFI"

def confidence_score(row):
    if row["NRFI %"] >= 60:  # NRFI confidence
        return round(row["NRFI %"], 1)
    else:                    # YRFI confidence is inverse
        return round(100 - row["NRFI %"], 1)

df["Result"] = df.apply(classify_result, axis=1)
df["Confidence %"] = df.apply(confidence_score, axis=1)

# ---- Color NRFI (red) / YRFI (green) ----
def color_result(val):
    if val == "NRFI":
        return "color: red; font-weight: bold"
    else:
        return "color: green; font-weight: bold"

styled_df = df[["Game Time", "Matchup", "Pitchers", "NRFI %", "Result", "Confidence %"]]\
    .style.applymap(color_result, subset=["Result"])

st.dataframe(styled_df, use_container_width=True, hide_index=True)
