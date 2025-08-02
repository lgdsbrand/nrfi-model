import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- PAGE CONFIG ---
st.set_page_config(page_title="NRFI / YRFI Model", layout="wide")
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BACK TO HOMEPAGE BUTTON ---
st.markdown("""
<div style="text-align: left; margin-bottom: 10px;">
    <a href="https://lineupwire.com" target="_self" 
       style="background-color: black; color: white; padding: 6px 16px; 
              border-radius: 12px; text-decoration: none;">
        ⬅ Back to Homepage
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='display: inline; white-space: nowrap;'>🔴🟢 NRFI / YRFI Model</h1>", unsafe_allow_html=True)

# --- LOAD LIVE MLB SCHEDULE ---
@st.cache_data(ttl=3600)
def fetch_nrfi_model():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    r = requests.get(url)
    data = r.json()
    
    est = pytz.timezone('US/Eastern')
    games = []
    for event in data.get("events", []):
        game_time_utc = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        game_time_est = game_time_utc.astimezone(est).strftime("%I:%M %p")

        competitions = event.get("competitions", [])[0]
        teams = competitions["competitors"]
        home_team = next(t["team"]["displayName"] for t in teams if t["homeAway"] == "home")
        away_team = next(t["team"]["displayName"] for t in teams if t["homeAway"] == "away")

        # --- SIMPLE NRFI/YRFI MODEL LOGIC (replace with your formula) ---
        confidence = 70 if len(home_team) % 2 == 0 else 55
        result = "NRFI" if confidence >= 60 else "YRFI"

        games.append([
            game_time_est,
            away_team,
            home_team,
            f"{confidence}%",
            result
        ])

    df = pd.DataFrame(games, columns=[
        "Game Time", "Away Team", "Home Team", "Confidence", "NRFI/YRFI"
    ])
    return df

df = fetch_nrfi_model()

# --- Color Cells for NRFI/YRFI Only ---
def highlight_nrfi(val):
    if val == "NRFI":
        return 'background-color: green; color: black; font-weight: bold;'
    elif val == "YRFI":
        return 'background-color: red; color: black; font-weight: bold;'
    return ''

styled_df = df.style.applymap(highlight_nrfi, subset=['NRFI/YRFI'])

st.dataframe(styled_df, use_container_width=True, hide_index=True)
