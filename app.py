import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="NRFI Model", layout="wide")

# -----------------------------
# CONFIG
# -----------------------------
REFRESH_HOURS = [0, 7, 12]  # refresh cycles

# -----------------------------
# FanDuel Scraper for MLB NRFI Games
# -----------------------------
@st.cache_data(ttl=3600)
def fetch_fanduel_data():
    """
    Scrape FanDuel MLB games for matchups, starting pitchers, and odds.
    Returns a DataFrame with real games only.
    """
    url = "https://sportsbook.fanduel.com/baseball/mlb"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    games = []

    # FanDuel event cards
    event_cards = soup.find_all("div", class_="event-card")
    for card in event_cards:
        teams = card.find_all("span", class_="event-card__name")
        if len(teams) < 2:
            continue

        away_team = teams[0].text.strip()
        home_team = teams[1].text.strip()
        matchup = f"{away_team} @ {home_team}"

        # Pitchers
        pitchers = card.find_all("div", class_="pitchers")
        away_pitcher = pitchers[0].text.strip() if pitchers else "TBD"
        home_pitcher = pitchers[1].text.strip() if len(pitchers) > 1 else "TBD"

        # Game time placeholder - FanDuel doesn't always provide
        game_time = datetime.now().strftime("%I:%M %p")  # convert to 12-hour

        # Odds (first available)
        odds_span = card.find("span", class_="sportsbook-odds")
        odds = -120
        if odds_span:
            try:
                odds = int(odds_span.text.replace("−", "-"))
            except:
                odds = -120

        games.append([game_time, matchup, away_pitcher, home_pitcher, odds])

    # Return empty DataFrame if no games
    df = pd.DataFrame(games, columns=["Game Time","Matchup","Away Pitcher","Home Pitcher","Book Odds"])
    return df

# -----------------------------
# NRFI Model Calculation
# -----------------------------
def calculate_nrfi_model(df):
    if df.empty:
        return df

    np.random.seed(42)  # For reproducibility

    # Simulated NRFI/YRFI probabilities (replace with your weighted model logic)
    df["NRFI_Prob"] = np.random.uniform(40, 85, len(df)) / 100.0

    # Determine pick and % chance
    df["NRFI/YRFI"] = df["NRFI_Prob"].apply(lambda x: "NRFI" if x >= 0.60 else "YRFI")
    df["% Chance"] = (df["NRFI_Prob"]*100).round(1)

    # Edge %
    def implied_prob(odds):
        return abs(odds)/(abs(odds)+100) if odds < 0 else 100/(odds+100)

    df["Edge %"] = ((df["NRFI_Prob"] - df["Book Odds"].apply(implied_prob)) * 100).round(1)

    return df[[
        "Game Time","Matchup","Away Pitcher","Home Pitcher",
        "NRFI/YRFI","% Chance","Book Odds","Edge %"
    ]]

# -----------------------------
# Weekly / Monthly Records
# -----------------------------
def weekly_monthly_records():
    st.subheader("📅 Weekly / Monthly Records (Start Empty)")

    weekly_df = pd.DataFrame(
        [[""]*7],
        columns=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        index=["ChatGPT NRFI"]
    )
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)

    monthly_df = pd.DataFrame(
        [[""]*1 for _ in range(12)],
        index=[
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ],
        columns=["Record"]
    )
    st.dataframe(monthly_df, use_container_width=True, hide_index=True)

# -----------------------------
# Color Styling
# -----------------------------
def highlight_nrfi(val, pick):
    try:
        val_f = float(val)
        if pick == "NRFI" and val_f >= 70:
            return "background-color: lightgreen"
        elif pick == "YRFI" and val_f >= 59:
            return "background-color: lightcoral"
    except:
        return ""
    return ""

# -----------------------------
# Streamlit Layout
# -----------------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tab1, tab2 = st.tabs(["Today's Model", "Weekly / Monthly Records"])

with tab1:
    st.subheader("Today's NRFI Model")
    df = fetch_fanduel_data()
    df = calculate_nrfi_model(df)

    if df.empty:
        st.info("No MLB games available right now. Check back at the next refresh cycle.")
    else:
        styled_df = df.style.apply(
            lambda x: [highlight_nrfi(v, x["NRFI/YRFI"]) for v in x["% Chance"]],
            axis=1
        )
        st.caption(f"Last Updated: {datetime.now().strftime('%I:%M %p EST')}")
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

with tab2:
    weekly_monthly_records()
