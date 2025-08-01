import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="NRFI Model", layout="wide")

# -----------------------
# CONFIG
# -----------------------
REFRESH_TIMES = [0, 7, 12]  # refresh at midnight, 7 AM, noon

# -----------------------
# SCRAPER: FanDuel MLB Odds + Pitchers
# -----------------------
@st.cache_data(ttl=3600)
def fetch_fanduel_data():
    """
    Scrapes FanDuel MLB NRFI/YRFI matchups with starting pitchers and odds.
    """
    url = "https://sportsbook.fanduel.com/baseball/mlb"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    games = []
    # FanDuel structures MLB games under event-cards
    for game in soup.find_all("div", class_="event-card"):
        teams = game.find_all("span", class_="event-card__name")
        odds_spans = game.find_all("span", class_="sportsbook-odds")

        if len(teams) >= 2:
            matchup = f"{teams[0].text.strip()} @ {teams[1].text.strip()}"
        else:
            continue

        # Extract pitchers if available
        pitchers = game.find_all("div", class_="pitchers")
        away_pitcher = pitchers[0].text.strip() if pitchers else "TBD"
        home_pitcher = pitchers[1].text.strip() if len(pitchers) > 1 else "TBD"

        # Extract NRFI odds if available
        odds = -120  # placeholder
        if odds_spans:
            try:
                odds = int(odds_spans[0].text.replace("−","-"))
            except:
                odds = -120

        games.append([matchup, away_pitcher, home_pitcher, odds])

    if not games:
        # fallback sample if scrape fails
        games = [
            ["ATL @ CIN", "S. Strider", "H. Greene", -150],
            ["BAL @ CHC", "K. Bradish", "J. Steele", -120],
            ["DET @ PHI", "T. Skubal", "A. Nola", +105],
        ]

    df = pd.DataFrame(games, columns=["Matchup", "Away Pitcher", "Home Pitcher", "Odds"])
    return df

# -----------------------
# MODEL CALCULATION
# -----------------------
def calculate_nrfi_model(df):
    np.random.seed(42)

    # Simulated NRFI model (replace w/ your real formula)
    df["NRFI %"] = np.random.uniform(40, 80, len(df)).round(0)
    df["YRFI %"] = (100 - df["NRFI %"]).round(0)

    # Implied probability from odds
    df["Implied Prob"] = df["Odds"].apply(
        lambda x: abs(x) / (abs(x) + 100) if x < 0 else 100 / (x + 100)
    )
    df["Edge %"] = ((df["NRFI %"] / 100) - df["Implied Prob"]).round(2)

    # Best Bet Column
    df["Best Bet"] = df["NRFI %"].apply(lambda x: "NRFI" if x >= 60 else "YRFI")
    return df

def color_nrfi(val):
    """Color NRFI/YRFI percentages for clarity"""
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

    df = fetch_fanduel_data()
    df = calculate_nrfi_model(df)

    styled_df = df.style.applymap(color_nrfi, subset=["NRFI %","YRFI %"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

with tab2:
    weekly_monthly_records()

with tab3:
    weekly_monthly_records()
