import pandas as pd
import numpy as np
import requests
from datetime import datetime

# CSV Files
TEAM_FILE = "team_nrfi.csv"
PITCHER_FILE = "pitcher_nrfi.csv"

def get_today_games():
    """Fetch today's MLB games from ESPN API with teams & probable pitchers."""
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()

    games = []
    for event in resp.get("events", []):
        comp = event["competitions"][0]
        home = comp["competitors"][0]
        away = comp["competitors"][1]

        # Game time in EST
        game_time = datetime.fromisoformat(comp["date"][:-1]).strftime("%I:%M %p")

        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Home Team": home["team"]["displayName"],
            "Away Team": away["team"]["displayName"],
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })
    return pd.DataFrame(games)

def calculate_nrfi(df):
    """Calculate NRFI/YRFI confidence using CSV stats."""
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    output = []
    for _, row in df.iterrows():
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        home_pitcher = row["Home Pitcher"]
        away_pitcher = row["Away Pitcher"]

        # Match team & pitcher stats
        team_home = teams[teams["Team"].str.contains(home_team.split()[-1], case=False, na=False)]
        team_away = teams[teams["Team"].str.contains(away_team.split()[-1], case=False, na=False)]
        pitch_home = pitchers[pitchers["Pitcher"].str.contains(home_pitcher.split()[0], case=False, na=False)]
        pitch_away = pitchers[pitchers["Pitcher"].str.contains(away_pitcher.split()[0], case=False, na=False)]

        # Default values if not found
        t_home_nrfi = team_home["NRFI%"].values[0] if not team_home.empty else 50
        t_away_nrfi = team_away["NRFI%"].values[0] if not team_away.empty else 50
        p_home_nrfi = pitch_home["NRFI%"].values[0] if not pitch_home.empty else 50
        p_away_nrfi = pitch_away["NRFI%"].values[0] if not pitch_away.empty else 50

        # Compute confidence score
        nrfi_confidence = round((t_home_nrfi + t_away_nrfi + p_home_nrfi + p_away_nrfi) / 4, 1)
        prediction = "NRFI" if nrfi_confidence >= 50 else "YRFI"

        output.append({
            "Game Time": row["Game Time"],
            "Matchup": f"{away_team} @ {home_team}",
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Prediction": prediction,
            "Confidence %": nrfi_confidence
        })

    return pd.DataFrame(output)
