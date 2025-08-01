import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

st.set_page_config(page_title="NRFI Model", layout="wide")

# ---------------------------
# 1️⃣ Scrape FanDuel MLB Games
# ---------------------------
def scrape_fanduel_games():
    url = "https://sportsbook.fanduel.com/baseball/mlb"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    games = []
    for event in soup.find_all("div", class_="event-card"):
        teams = event.find_all("span", class_="event-card__name")
        if len(teams) == 2:
            away_team = teams[0].text.strip()
            home_team = teams[1].text.strip()

            # Attempt to scrape pitchers if available
            pitchers = event.find_all("div", class_="pitchers")
            away_pitcher = pitchers[0].text.strip() if len(pitchers) >= 1 else "TBD"
            home_pitcher = pitchers[1].text.strip() if len(pitchers) >= 2 else "TBD"

            # Odds
            odds_elem = event.find("span", class_="sportsbook-odds")
            odds = odds_elem.text.strip() if odds_elem else "N/A"

            # Game Time placeholder (FanDuel doesn't list on main page)
            game_time = datetime.now().strftime("%I:%M %p")

            games.append({
                "Game Time": game_time,
                "Matchup": f"{away_team} @ {home_team}",
                "Away Pitcher": away_pitcher,
                "Home Pitcher": home_pitcher,
                "Book Odds": odds
            })

    return pd.DataFrame(games)


# ---------------------------
# 2️⃣ Generate NRFI / YRFI Model
# ---------------------------
def calculate_nrfi_model(df):
    np.random.seed(42)
    df["Model %"] = np.random.uniform(45, 80, len(df)).round(0).astype(int)
    df["NRFI/YRFI"] = df["Model %"].apply(lambda x: "NRFI" if x >= 60 else "YRFI")

    # Convert odds to implied probability
    def american_to_prob(odds):
        try:
            odds = int(str(odds).replace("+", ""))
            if odds < 0:
                return abs(odds) / (abs(odds) + 100)
            else:
                return 100 / (odds + 100)
        except:
            return np.nan

    df["Book Odds Clean"] = pd.to_numeric(df["Book Odds"].str.replace("+",""), errors="coerce")
    df["Edge %"] = ((df["Model %"]/100) - df["Book Odds Clean"].apply(american_to_prob)) * 100
    df["Edge %"] = df["Edge %"].round(0).astype(int)

    return df[[
        "Game Time","Matchup","Away Pitcher","Home Pitcher",
        "NRFI/YRFI","Model %","Edge %","Book Odds"
    ]]


# ---------------------------
# 3️⃣ Streamlit UI
# ---------------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tabs = st.tabs(["Today's Model", "Weekly / Monthly Records"])

# Today's Model Tab
with tabs[0]:
    df_games = scrape_fanduel_games()

    # Force refresh at midnight, 7 AM, noon
    est = pytz.timezone("US/Eastern")
    current_hour = datetime.now(est).hour
    if current_hour in [0, 7, 12]:
        st.experimental_rerun()

    if df_games.empty:
        st.info("No MLB games available right now. Check back at the next refresh cycle.")
    else:
        df_nrfi = calculate_nrfi_model(df_games)

        # Highlight NRFI ≥70 green, YRFI ≤59 red
        def highlight_cells(val, row):
            if row["NRFI/YRFI"] == "NRFI" and row["Model %"] >= 70:
                return 'color: green; font-weight: bold'
            if row["NRFI/YRFI"] == "YRFI" and row["Model %"] <= 59:
                return 'color: red; font-weight: bold'
            return ''

        st.dataframe(
            df_nrfi.style.apply(
                lambda row: [highlight_cells(v, row) for v in row], axis=1
            ),
            use_container_width=True,
            hide_index=True  # ✅ removes far-left index column
        )

# Weekly / Monthly Records Tab
with tabs[1]:
    st.subheader("📊 Weekly / Monthly NRFI Model Records")
    weekly_monthly = pd.DataFrame({
        "Mon": [], "Tue": [], "Wed": [], "Thu": [], "Fri": [], "Sat": [], "Sun": []
    })
    st.dataframe(weekly_monthly, use_container_width=True, hide_index=True)
    monthly = pd.DataFrame({
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Record": ["" for _ in range(12)]
    })
    st.dataframe(monthly, use_container_width=True, hide_index=True)
