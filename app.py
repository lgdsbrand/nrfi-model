import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------------------
# HEADER
# ---------------------------
st.markdown(
    """
    <style>
        .back-btn {
            background-color: black;
            color: white;
            padding: 8px 20px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: bold;
        }
        .back-btn:hover {
            background-color: #333;
        }
        .dataframe tbody tr td {
            text-align: center;
            font-weight: bold;
        }
    </style>
    <a class="back-btn" href="https://lineupwire.com">⬅ Back to Homepage</a>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1>🔴🟢 NRFI / YRFI Model</h1>", unsafe_allow_html=True)

# ---------------------------
# ESPN API - MLB Games Today
# ---------------------------
today = datetime.now().strftime("%Y%m%d")
url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
data = requests.get(url).json()

games = []
for event in data.get("events", []):
    game_time = datetime.fromisoformat(event["date"].replace("Z", "+00:00")).strftime("%I:%M %p ET")
    away_team = event["competitions"][0]["competitors"][1]["team"]["displayName"]
    home_team = event["competitions"][0]["competitors"][0]["team"]["displayName"]
    
    # Dummy NRFI/YRFI confidence calculation (replace with your formula)
    nrfi_conf = (len(away_team) + len(home_team)) % 100
    yrfi_conf = 100 - nrfi_conf
    best_pick = "NRFI" if nrfi_conf >= yrfi_conf else "YRFI"
    conf = max(nrfi_conf, yrfi_conf)
    
    # Color code cells
    color = "background-color: red; color: black" if best_pick == "NRFI" else "background-color: green; color: black"
    
    games.append([
        game_time, away_team, home_team, best_pick, conf, color
    ])

columns = ["Game Time", "Away Team", "Home Team", "Pick", "Confidence %", "color"]

df = pd.DataFrame(games, columns=columns)
df = df.sort_values("Confidence %", ascending=False)

# Apply color to Pick cell
def color_cells(val, color):
    return color if val else ""

styled = df.style.apply(lambda x: [x["color"]] * len(x), axis=1)
styled = styled.hide(axis="columns", names="color")

st.dataframe(styled, hide_index=True, use_container_width=True)
