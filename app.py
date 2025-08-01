import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import random

st.set_page_config(page_title="NRFI Model", layout="wide")

# -----------------------------
# Utility Functions
# -----------------------------
def fetch_espn_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url)
    data = resp.json()
    
    games = []
    for event in data.get("events", []):
        comp = event.get("competitions", [])[0]
        competitors = comp.get("competitors", [])

        # Ensure correct home/away mapping
        away = next((t for t in competitors if t["homeAway"] == "away"), None)
        home = next((t for t in competitors if t["homeAway"] == "home"), None)

        if not away or not home:
            continue

        game_time = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        game_time = game_time.astimezone(pytz.timezone("US/Eastern")).strftime("%I:%M %p ET")

        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Away Pitcher": away_pitcher,
            "Home Pitcher": home_pitcher
        })
    return pd.DataFrame(games)

def calculate_nrfi_confidence(row):
    # Simulated model % for now (replace with real formula when ready)
    confidence = random.uniform(40, 85)
    return round(confidence)

def determine_nrfi_label(conf):
    if conf >= 70:
        return "NRFI"
    elif conf <= 59:
        return "YRFI"
    else:
        return "Lean"

def color_confidence(val):
    if isinstance(val, int):
        if val >= 70:
            return "color: green; font-weight: bold"
        elif val <= 59:
            return "color: red; font-weight: bold"
    return ""

# -----------------------------
# Auto-refresh Logic
# -----------------------------
est = pytz.timezone("US/Eastern")
current_hour = datetime.now(est).hour
# Refresh at midnight, 7am, noon, and every hour
if current_hour in [0, 7, 12] or datetime.now().minute == 0:
    st.experimental_rerun()

# -----------------------------
# Main App Layout
# -----------------------------
st.title("🟢 NRFI Model (No Run First Inning)")

tab1, tab2 = st.tabs(["Today's Model", "Weekly / Monthly Records"])

with tab1:
    df_games = fetch_espn_games()

    if df_games.empty:
        st.info("No MLB games available right now. Check back at the next refresh cycle.")
    else:
        # Compute NRFI Confidence
        df_games["Confidence %"] = df_games.apply(lambda x: calculate_nrfi_confidence(x), axis=1)
        df_games["NRFI/YRFI"] = df_games["Confidence %"].apply(lambda x: determine_nrfi_label(x))
        df_games["Book Odds"] = ""
        df_games["Edge %"] = ""

        # Reorder columns
        df_games = df_games[[
            "Game Time", "Matchup", "Away Pitcher", "Home Pitcher",
            "NRFI/YRFI", "Confidence %", "Book Odds", "Edge %"
        ]]

        st.dataframe(
            df_games.style.applymap(color_confidence, subset=["Confidence %"]),
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.subheader("📊 Weekly / Monthly Records")
    records = pd.DataFrame({
        "Period": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
                   "January", "February", "March", "April", "May",
                   "June", "July", "August", "September", "October", "November", "December"],
        "Record": ["" for _ in range(19)]
    })
    st.dataframe(records, use_container_width=True, hide_index=True)
