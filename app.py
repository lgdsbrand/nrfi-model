import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="NRFI Model", layout="wide")

# -------------------------
# Functions
# -------------------------
def get_today_nrfi_data():
    """
    Simulate fetching today's NRFI/YRFI model data.
    Replace with your actual model or scraping logic.
    """
    # Sample data
    data = {
        "Game Time": ["1:05 PM", "4:10 PM", "7:05 PM"],
        "Matchup": ["ATL @ CIN", "NYY @ BOS", "LAD @ SF"],
        "Away Pitcher": ["Fried", "Cole", "Kershaw"],
        "Home Pitcher": ["Greene", "Bello", "Webb"],
        "NRFI %": [0.55, 0.78, 0.69],
        "YRFI %": [0.45, 0.22, 0.31],
        "Book Odds": [-150, -120, 105],
    }

    df = pd.DataFrame(data)

    # Implied probability from odds
    df["Implied Prob"] = df["Book Odds"].apply(lambda x: abs(x) / (abs(x)+100) if x<0 else 100/(x+100))
    # Edge percentage
    df["Edge %"] = ((df["NRFI %"]) - df["Implied Prob"]) * 100

    # Clean up formatting
    df["NRFI %"] = (df["NRFI %"]*100).round(1)
    df["YRFI %"] = (df["YRFI %"]*100).round(1)
    df["Implied Prob"] = (df["Implied Prob"]*100).round(1)
    df["Edge %"] = df["Edge %"].round(1)

    # Ensure all expected columns exist
    for col in ["Game Time","Matchup","Away Pitcher","Home Pitcher","Book Odds","NRFI %","YRFI %","Implied Prob","Edge %"]:
        if col not in df.columns:
            df[col] = "TBD"

    return df

def display_model_table(df):
    """
    Display the NRFI model table with color highlights.
    """
    def highlight_cells(val, column):
        if column == "NRFI %":
            if val >= 70:
                return 'color: green; font-weight: bold;'
        if column == "YRFI %":
            if val >= 70:
                return 'color: red; font-weight: bold;'
        return ''

    styled_df = df.style.applymap(lambda x: highlight_cells(x, "NRFI %"), subset=["NRFI %"])\
                        .applymap(lambda x: highlight_cells(x, "YRFI %"), subset=["YRFI %"])

    st.dataframe(styled_df, use_container_width=True)

# -------------------------
# Page Layout
# -------------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tab1, tab2 = st.tabs(["Today's Model", "Weekly / Monthly Records"])

# -------------------------
# Tab 1: Today's Model
# -------------------------
with tab1:
    st.subheader("Today's NRFI Model")
    df = get_today_nrfi_data()
    display_model_table(df)

# -------------------------
# Tab 2: Weekly / Monthly Records
# -------------------------
with tab2:
    st.subheader("Weekly / Monthly Records")
    week_data = pd.DataFrame({
        "Mon": ["1-1"], "Tue": ["2-0"], "Wed": ["1-0"], "Thu": ["0-0"],
        "Fri": ["0-0"], "Sat": ["0-0"], "Sun": ["0-0"]
    }, index=["ChatGPT NRFI"])
    month_data = pd.DataFrame({
        "Jan": ["0-0"], "Feb": ["0-0"], "Mar": ["0-0"], "Apr": ["0-0"],
        "May": ["0-0"], "Jun": ["0-0"], "Jul": ["0-0"], "Aug": ["0-0"],
        "Sep": ["0-0"], "Oct": ["0-0"], "Nov": ["0-0"], "Dec": ["0-0"]
    }, index=["ChatGPT NRFI"])

    st.markdown("**Weekly Record**")
    st.dataframe(week_data, use_container_width=True)

    st.markdown("**Monthly Record**")
    st.dataframe(month_data, use_container_width=True)
