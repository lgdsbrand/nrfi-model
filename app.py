import streamlit as st
import pandas as pd
import datetime
import requests
import numpy as np

st.set_page_config(page_title="NRFI Model", layout="wide")

# -----------------------
# CONFIG
# -----------------------
REFRESH_TIMES = [0, 7, 12]  # refresh at midnight, 7 AM, noon

# -----------------------
# UTILS
# -----------------------
@st.cache_data(ttl=3600)  # refresh every hour
def fetch_fanduel_data():
    """
    Scrapes FanDuel for MLB matchups, starting pitchers, and odds (mock endpoint).
    Replace this with real FanDuel API or odds scraper logic.
    """
    today = datetime.datetime.now().strftime("%Y%m%d")

    # Simulated data (replace with your scraper)
    data = [
        ["ATL @ CIN", "S. Strider", "H. Greene", -150],
        ["BAL @ CHC", "K. Bradish", "J. Steele", -120],
        ["DET @ PHI", "T. Skubal", "A. Nola", +105],
        ["MIL @ WSH", "C. Burnes", "M. Gore", -135],
        ["KC @ TOR", "B. Singer", "K. Gausman", +110],
    ]

    df = pd.DataFrame(data, columns=["Matchup", "Away Pitcher", "Home Pitcher", "Odds"])
    return df

def calculate_nrfi_model(df):
    np.random.seed(42)

    # Mock NRFI % (replace with your real formula)
    df["NRFI %"] = np.random.uniform(40, 80, len(df)).round(0)
    df["YRFI %"] = (100 - df["NRFI %"]).round(0)

    # Edge % based on odds and NRFI %
    # Implied probability from odds
    df["Implied Prob"] = df["Odds"].apply(
        lambda x: abs(x) / (abs(x) + 100) if x < 0 else 100 / (x + 100)
    )
    df["Edge %"] = ((df["NRFI %"] / 100) - df["Implied Prob"]).round(2)

    # NRFI or YRFI recommendation
    df["Best Bet"] = df["NRFI %"].apply(lambda x: "NRFI" if x >= 60 else "YRFI")
    return df

def color_nrfi(val):
    """Green if NRFI strong, Red if YRFI strong."""
    try:
        val = float(val)
        if val >= 70:
            return "color: green; font-weight:bold"
        elif val <= 40:
            return "color: red; font-weight:bold"
        else:
            return ""
    except:
        return ""

# -----------------------
# WEEKLY & MONTHLY RECORDS
# -----------------------
def weekly_monthly_records():
    st.subheader("📅 Weekly Records")
    weekly_df = pd.DataFrame(
        [["1-1", "2-0", "1-0", "", "", "", ""]],
        columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        index=["ChatGPT NRFI"]
    )
    st.table(weekly_df)

    st.subheader("📊 Monthly Records")
    monthly_df = pd.DataFrame(
        [[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""],[""]],
        index=[
            "Jan","Feb","Mar","Apr","May","June","July",
            "Aug","Sept","Oct","Nov","Dec"
        ],
        columns=["Record"]
    )
    st.table(monthly_df)

# -----------------------
# APP LAYOUT
# -----------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tab1, tab2, tab3 = st.tabs(["Today's Model", "Weekly Record", "Monthly Record"])

with tab1:
    st.subheader("Today's NRFI Model")

    # Fetch and calculate
    df = fetch_fanduel_data()
    df = calculate_nrfi_model(df)

    # Style table
    styled_df = df.style.applymap(color_nrfi, subset=["NRFI %","YRFI %"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

with tab2:
    weekly_monthly_records()

with tab3:
    weekly_monthly_records()
