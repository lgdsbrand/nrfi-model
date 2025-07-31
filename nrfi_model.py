import streamlit as st
import pandas as pd
import datetime
import requests
import numpy as np

def get_today_espn_games():
    today = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    response = requests.get(url)
    games = response.json().get("events", [])

    game_list = []
    for game in games:
        game_time = datetime.datetime.strptime(game.get('date'), "%Y-%m-%dT%H:%MZ").strftime("%I:%M %p")
        teams = game["competitions"][0]["competitors"]
        home = next(team for team in teams if team["homeAway"] == "home")
        away = next(team for team in teams if team["homeAway"] == "away")

        away_pitcher = away.get("probablePitcher", {}).get("fullName") if away.get("probablePitcher") else "TBD"
        home_pitcher = home.get("probablePitcher", {}).get("fullName") if home.get("probablePitcher") else "TBD"

        game_list.append({
            "game_time": game_time,
            "matchup": f"{away['team']['abbreviation']} @ {home['team']['abbreviation']}",
            "away_team": away["team"]["abbreviation"],
            "home_team": home["team"]["abbreviation"],
            "away_pitcher": away_pitcher,
            "home_pitcher": home_pitcher
        })

    return pd.DataFrame(game_list)


def generate_model_nrfi(df):
    # Simulated NRFI % model (can replace with real logic later)
    np.random.seed(42)
    df["model_nrfi_percent"] = np.clip(
        0.5 + np.random.normal(0, 0.1, len(df)), 0.1, 0.95
    )
    df["model_nrfi_percent"] = (df["model_nrfi_percent"] * 100).round(1)
    return df

def render():
    st.title("🟢 NRFI Model (No Run First Inning)")

    df = get_today_espn_games()
    if df.empty:
        st.warning("No games found for today.")
        return

    df = generate_model_nrfi(df)

    # Drop unneeded columns
    df = df.drop(columns=["away_team", "home_team"], errors="ignore")

    # Rename for cleaner display
    df = df.rename(columns={
        "game_time": "Time",
        "matchup": "Matchup",
        "away_pitcher": "Away Pitcher",
        "home_pitcher": "Home Pitcher",
        "model_nrfi_percent": "NRFI %"
    })

    # Color logic: green ≥ 55%, red ≤ 45%
    def highlight(val):
        if val >= 55:
            color = "green"
        elif val <= 45:
            color = "red"
        else:
            color = "black"
        return f"color: {color}; font-weight: bold"

    styled_df = df.style.applymap(highlight, subset=["NRFI %"])

    # Clean display (no row numbers or scrollbars)
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
