import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import math

# -------------------------------
# PAGE CONFIG
# -------------------------------
def run_nrfi_app():
    st.title("⚾ LineupWire NRFI Model")

    # Toggle for Today vs Records
    view = st.radio("Select View", ["Today’s Model", "Records"], horizontal=True)

    # Cache data with 1-hour TTL
    @st.cache_data(ttl=3600)
    def fetch_mlb_data():
        today = datetime.now().strftime("%Y%m%d")
        url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
        r = requests.get(url)
        data = r.json()

        games = []
        for event in data.get("events", []):
            try:
                comp = event["competitions"][0]
                home = comp["competitors"][0]
                away = comp["competitors"][1]

                game_time = datetime.fromisoformat(event["date"][:-1]).strftime("%I:%M %p")

                home_team = home["team"]["displayName"]
                away_team = away["team"]["displayName"]

                home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
                away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

                games.append({
                    "time": game_time,
                    "matchup": f"{away_team} @ {home_team}",
                    "pitching": f"{away_pitcher} vs {home_pitcher}",
                    "away_team": away_team,
                    "home_team": home_team
                })
            except:
                continue

        return games

    # -------------------------------
    # NRFI Probability Formula
    # -------------------------------
    def nrfi_probability(game):
        # Placeholder for your full weighted formula
        # Replace with real stat integration (Team 1st inning RPG, SP NRFI%, park factor)
        # Example weighting logic
        import random
        base_prob = random.uniform(0.45, 0.85)  # 45% to 85% NRFI
        return round(base_prob * 100)

    # -------------------------------
    # FanDuel Odds & Edge
    # -------------------------------
    def get_fd_odds(matchup):
        # Placeholder odds; can integrate scrape later
        import random
        return random.choice([-150, -130, -120, +100, +110])

    def implied_prob(odds):
        return 100/(odds+100) if odds>0 else abs(odds)/(abs(odds)+100)

    def calc_edge(model_prob, odds):
        imp = implied_prob(odds)
        return round((model_prob/100 - imp)*100, 1)

    # -------------------------------
    # Build Today's Model Table
    # -------------------------------
    games = fetch_mlb_data()

    if view == "Today’s Model":
        rows = []
        for g in games:
            nrfi_prob = nrfi_probability(g)
            pick = "NRFI" if nrfi_prob >= 60 else "YRFI"
            confidence = min(10, max(1, nrfi_prob // 10))
            odds = get_fd_odds(g["matchup"])
            edge = calc_edge(nrfi_prob, odds)

            rows.append([
                g["time"],
                g["matchup"],
                g["pitching"],
                pick,
                f"{nrfi_prob}%",
                confidence,
                odds,
                f"{edge}%"
            ])

        df = pd.DataFrame(rows, columns=[
            "Time","Matchup","Pitching Matchup","Model Pick",
            "Model %","Confidence (1-10)","FanDuel Odds","Edge %"
        ])

        def highlight_nrfi(val, pick):
            try:
                num = int(val.replace("%",""))
                if pick == "NRFI" and num >= 70:
                    return "background-color: lightgreen"
                elif pick == "YRFI" and num >= 70:
                    return "background-color: lightcoral"
            except:
                return ""
            return ""

        styled_df = df.style.apply(
            lambda x: [highlight_nrfi(v, x["Model Pick"]) for v in x["Model %"]],
            axis=1
        )

        st.caption(f"Last Updated: {datetime.now().strftime('%I:%M %p EST')}")
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    else:
        st.caption(f"Last Updated: {datetime.now().strftime('%I:%M %p EST')}")

        # Empty records table structure
        weekly = pd.DataFrame(columns=["Week","Wins","Losses","Win %"])
        monthly = pd.DataFrame(columns=["Month","Wins","Losses","Win %"])

        st.subheader("Weekly Record (Mon-Sun)")
        st.dataframe(weekly, use_container_width=True, hide_index=True)

        st.subheader("Monthly Record (Month-to-Date)")
        st.dataframe(monthly, use_container_width=True, hide_index=True)
