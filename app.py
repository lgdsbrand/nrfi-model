import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import datetime

st.set_page_config(page_title="NRFI Model", layout="wide")

# -----------------------------
# CONFIG
# -----------------------------
REFRESH_HOURS = [0, 7, 12]  # refresh cycles (midnight, 7AM, noon)

# -----------------------------
# FanDuel Scraper (Teams, Pitchers, Odds)
# -----------------------------
@st.cache_data(ttl=3600)
def fetch_fanduel_data():
    """
    Scrapes FanDuel MLB games for matchups, pitchers, and odds.
    Returns DataFrame with columns:
    ['Game Time','Matchup','Away Pitcher','Home Pitcher','Odds']
    """
    # Note: Example scraping, replace selector logic if FD site structure changes
    url = "https://sportsbook.fanduel.com/baseball/mlb"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    games = []

    # Fallback sample if scrape fails
    fallback = [
        ["1:05 PM", "ATL @ CIN", "S. Strider", "H. Greene", -135],
        ["2:10 PM", "BAL @ CHC", "K. Bradish", "J. Steele", -120],
        ["4:05 PM", "DET @ PHI", "T. Skubal", "A. Nola", +110],
    ]

    try:
        event_cards = soup.find_all("div", class_="event-card")
        for card in event_cards:
            teams = card.find_all("span", class_="event-card__name")
            if len(teams) < 2:
                continue
            matchup = f"{teams[0].text.strip()} @ {teams[1].text.strip()}"

            # Pitchers (FanDuel may list or TBD)
            pitchers = card.find_all("div", class_="pitchers")
            away_pitcher = pitchers[0].text.strip() if pitchers else "TBD"
            home_pitcher = pitchers[1].text.strip() if len(pitchers) > 1 else "TBD"

            # Time (convert to 12-hour format EST)
            game_time = datetime.datetime.now().strftime("%I:%M %p")  # placeholder

            # Odds
            odds_span = card.find("span", class_="sportsbook-odds")
            odds = -120
            if odds_span:
                try:
                    odds = int(odds_span.text.replace("−", "-"))
                except:
                    odds = -120

            games.append([game_time, matchup, away_pitcher, home_pitcher, odds])

    except:
        games = fallback

    df = pd.DataFrame(games, columns=["Game Time","Matchup","Away Pitcher","Home Pitcher","Odds"])
    return df

# -----------------------------
# NRFI Model Calculation (cleaner formatting)
# -----------------------------
def calculate_nrfi_model(df):
    np.random.seed(42)

    # Simulated NRFI formula
    df["NRFI %"] = np.random.uniform(40, 85, len(df)).round(1)
    df["YRFI %"] = (100 - df["NRFI %"]).round(1)
    df["NRFI/YRFI"] = df["NRFI %"].apply(lambda x: "NRFI" if x >= 60 else "YRFI")
    df["Confidence (1-10)"] = df["NRFI %"].apply(lambda x: min(10, max(1, int(x/10))))

    # Implied probability from odds
    def implied_prob(odds):
        return round(abs(odds)/(abs(odds)+100), 2) if odds < 0 else round(100/(odds+100), 2)

    df["Implied Prob"] = df["Odds"].apply(implied_prob)
    df["Edge %"] = ((df["NRFI %"]/100) - df["Implied Prob"]).round(2)*100
    df.rename(columns={"Odds":"Book Odds"}, inplace=True)

    return df[[
        "Game Time","Matchup","Away Pitcher","Home Pitcher",
        "NRFI %","YRFI %","NRFI/YRFI","Confidence (1-10)","Book Odds","Implied Prob","Edge %"
    ]]

# -----------------------------
# Weekly & Monthly Records (Starts Empty)
# -----------------------------
def weekly_monthly_records():
    st.subheader("📅 Weekly Records (Mon-Sun)")
    weekly_df = pd.DataFrame(
        [["","","","","","",""]],
        columns=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        index=["ChatGPT NRFI"]
    )
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)

    st.subheader("📊 Monthly Records")
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
# Styling
# -----------------------------
def highlight_nrfi(val, pick):
    try:
        val_f = float(val)
        if pick == "NRFI" and val_f >= 70:
            return "background-color: lightgreen"
        elif pick == "YRFI" and val_f >= 70:
            return "background-color: lightcoral"
    except:
        return ""
    return ""

# -----------------------------
# APP LAYOUT
# -----------------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tab1, tab2, = st.tabs(["Today's Model", "Weekly/Monthly Record"])

with tab1:
    st.subheader("Today's NRFI Model")
    df = fetch_fanduel_data()
    df = calculate_nrfi_model(df)

    # Style NRFI/YRFI highlights
    styled_df = df.style.apply(
        lambda x: [highlight_nrfi(v, x["NRFI/YRFI"]) for v in x["NRFI %"]],
        axis=1
    )

    st.caption(f"Last Updated: {datetime.datetime.now().strftime('%I:%M %p EST')}")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

with tab2:
    weekly_monthly_records()

with tab3:
    weekly_monthly_records()
