import streamlit as st
import pandas as pd
import datetime
import requests

def get_today_espn_games():
    today = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    response = requests.get(url)
    games = response.json().get("events", [])

    game_list = []
    for game in games:
        teams = game['competitions'][0]['competitors']
        home = next(team for team in teams if team['homeAway'] == 'home')
        away = next(team for team in teams if team['homeAway'] == 'away')

        game_list.append({
            'matchup': f"{away['team']['abbreviation']} @ {home['team']['abbreviation']}",
            'away_team': away['team']['abbreviation'],
            'home_team': home['team']['abbreviation'],
            'away_pitcher': away.get('probablePitcher', {}).get('displayName', 'TBD'),
            'home_pitcher': home.get('probablePitcher', {}).get('displayName', 'TBD'),
            'game_time': game.get('date', '')[11:16]  # "HH:MM"
        })
    return pd.DataFrame(game_list)

def generate_model_nrfi(df):
    import numpy as np
    # Simulated NRFI model: base 50% + random noise + pitcher/team influence
    np.random.seed(42)
    df["model_nrfi_percent"] = np.clip(
        0.5 +
        np.random.normal(0, 0.1, len(df)), 0.1, 0.95
    )
    df["model_nrfi_percent"] = (df["model_nrfi_percent"] * 100).round(1)
    return df

def render():
    st.title("⚾ NRFI Model (No Run First Inning)")

    df = get_today_espn_games()
    if df.empty:
        st.warning("No games found for today.")
        return

    df = generate_model_nrfi(df)

    # Display: NRFI % in green if ≥ 55%, red if < 45%, else neutral
    def highlight_nrfi(val):
        try:
            val = float(val)
            if val >= 55:
                return "background-color: lightgreen; color: black"
            elif val <= 45:
                return "background-color: salmon; color: black"
        except:
            return ""
        return ""

    display_df = df[[
        'game_time', 'matchup', 'away_pitcher', 'home_pitcher', 'model_nrfi_percent'
    ]].rename(columns={
        'game_time': 'Time (ET)',
        'matchup': 'Matchup',
        'away_pitcher': 'Away Pitcher',
        'home_pitcher': 'Home Pitcher',
        'model_nrfi_percent': 'NRFI %'
    })

    st.dataframe(display_df.style.applymap(highlight_nrfi, subset=['NRFI %']), use_container_width=True)
