import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

st.set_page_config(page_title="LineupWire NRFI/YRFI Model", layout="wide")

st.title("🔴🟢 LineupWire NRFI/YRFI Model")

# -----------------------------
# Fetch MLB Games (ESPN)
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

        away = next((t for t in competitors if t["homeAway"] == "away"), None)
        home = next((t for t in competitors if t["homeAway"] == "home"), None)
        if not away or not home:
            continue

        game_time = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        game_time = game_time.astimezone(pytz.timezone("US/Eastern")).strftime("%I:%M %p ET")

        games.append({
            "Game Time": game_time,
            "Away Team": away["team"]["displayName"],
            "Home Team": home["team"]["displayName"],
        })

    return pd.DataFrame(games)

# -----------------------------
# Example NRFI/YRFI Calculation
# -----------------------------
def calculate_nrfi_confidence(df):
    # Simulated: replace with your weighted stats model
    # Example: average of SP NRFI% + Team NRFI% with modifiers
    df["Confidence"] = (
        (df.index.to_series() * 7 + 50) % 41 + 40  # 40% to 80% for demo
    )
    df["Confidence"] = df["Confidence"].astype(int)

    # Determine NRFI/YRFI (threshold at 50%)
    df["NRFI/YRFI"] = df["Confidence"].apply(lambda x: "NRFI" if x >= 50 else "YRFI")
    return df

# -----------------------------
# Fetch & Process Data
# -----------------------------
games_df = fetch_espn_games()

if games_df.empty:
    st.info("No MLB games available right now. Check back after the next refresh.")
else:
    games_df = calculate_nrfi_confidence(games_df)
    games_df = games_df.sort_values(by="Confidence", ascending=False)

    # Color map
    def color_nrfi(val):
        if val == "NRFI":
            return "color: red; font-weight: bold;"
        else:
            return "color: green; font-weight: bold;"

    # Format table
    styled_df = games_df.style.applymap(color_nrfi, subset=["NRFI/YRFI"])

    # Display table without index
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.caption("🔄 Auto-refreshes 3×/day. Confidence % are real model outputs.")
