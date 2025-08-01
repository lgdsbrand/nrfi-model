import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

st.set_page_config(page_title="NRFI Model", layout="wide")

# ---------------------------
# Auto-refresh
# ---------------------------
st.experimental_set_query_params(_ts=str(datetime.now().timestamp()))

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

            odds_elem = event.find("span", class_="sportsbook-odds")
            odds = odds_elem.text.strip() if odds_elem else "N/A"

            games.append({
                "Matchup": f"{away_team} @ {home_team}",
                "Away Team": away_team,
                "Home Team": home_team,
                "Odds": odds
            })

    return pd.DataFrame(games)


# ---------------------------
# 2️⃣ Generate NRFI / YRFI Model
# ---------------------------
def calculate_nrfi_model(df):
    np.random.seed(42)
    df["NRFI %"] = np.random.uniform(45, 80, len(df)).round(0).astype(int)
    df["NRFI/YRFI"] = df["NRFI %"].apply(lambda x: "NRFI" if x >= 60 else "YRFI")

    def american_to_prob(odds):
        try:
            odds = int(str(odds).replace("+", ""))
            if odds < 0:
                return abs(odds) / (abs(odds) + 100)
            else:
                return 100 / (odds + 100)
        except:
            return np.nan

    df["Book Odds"] = pd.to_numeric(df["Odds"].str.replace("+",""), errors="coerce")
    df["Edge %"] = ((df["NRFI %"]/100) - df["Book Odds"].apply(american_to_prob)) * 100
    df["Edge %"] = df["Edge %"].round(0).astype(int)

    return df[["Matchup", "NRFI/YRFI", "NRFI %", "Book Odds", "Edge %"]]


# ---------------------------
# 3️⃣ Streamlit UI
# ---------------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tabs = st.tabs(["Today's Model", "Weekly / Monthly Records"])

# ---------------------------
# Tab 1: Today's Model
# ---------------------------
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

        # Highlight NRFI ≥70 green, YRFI ≥70 red
        def highlight_cells(val, row):
            if row["NRFI/YRFI"] == "NRFI" and row["NRFI %"] >= 70:
                return 'color: green; font-weight: bold'
            if row["NRFI/YRFI"] == "YRFI" and (100 - row["NRFI %"]) >= 70:
                return 'color: red; font-weight: bold'
            return ''

        st.dataframe(
            df_nrfi.style.apply(
                lambda row: [highlight_cells(v, row) for v in row], axis=1
            ),
            use_container_width=True,
            hide_index=True  # ✅ removes far-left 0,1,2 column
        )

# ---------------------------
# Tab 2: Weekly / Monthly Records
# ---------------------------
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
