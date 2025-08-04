import pandas as pd
import numpy as np
import random
from datetime import datetime

TEAM_FILE = "team_nrfi.csv"
PITCHER_FILE = "pitcher_nrfi.csv"

def get_today_games():
    """
    Simulate daily games with team & pitcher NRFI data.
    Replace this with ESPN scraping if needed.
    """
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    games = []
    # Pair sequentially for simplicity
    for i in range(0, min(len(teams), len(pitchers)), 2):
        home_team = teams.iloc[i % len(teams)]
        away_team = teams.iloc[(i+1) % len(teams)]
        home_pitcher = pitchers.iloc[i % len(pitchers)]
        away_pitcher = pitchers.iloc[(i+1) % len(pitchers)]

        game_time = datetime.now().strftime("%I:%M %p")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away_team['Team']} @ {home_team['Team']}",
            "Pitchers": f"{away_pitcher['Pitcher']} vs {home_pitcher['Pitcher']}",
            "Home Team": home_team['Team'],
            "Away Team": away_team['Team'],
            "Home Pitcher": home_pitcher['Pitcher'],
            "Away Pitcher": away_pitcher['Pitcher'],
        })
    return pd.DataFrame(games)

def calculate_nrfi(df):
    """
    Calculate NRFI/YRFI prediction with confidence.
    NRFI = Red, YRFI = Green
    """
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    predictions = []
    for _, row in df.iterrows():
        home_team = row['Home Team']
        away_team = row['Away Team']
        home_pitcher = row['Home Pitcher']
        away_pitcher = row['Away Pitcher']

        # Skip if TBD pitcher
        if "TBD" in home_pitcher or "TBD" in away_pitcher:
            predictions.append({"Prediction": "", "Confidence %": ""})
            continue

        # Pull stats
        home_team_stats = teams[teams['Team'] == home_team].iloc[0]
        away_team_stats = teams[teams['Team'] == away_team].iloc[0]
        home_pitcher_stats = pitchers[pitchers['Pitcher'] == home_pitcher].iloc[0]
        away_pitcher_stats = pitchers[pitchers['Pitcher'] == away_pitcher].iloc[0]

        # Weighted confidence: average of NRFI%
        confidence = (
            home_team_stats['NRFI%'] +
            away_team_stats['NRFI%'] +
            home_pitcher_stats['NRFI%'] +
            away_pitcher_stats['NRFI%']
        ) / 4

        confidence = round(confidence, 1)

        # Decide NRFI or YRFI
        if confidence >= 60:
            prediction = "NRFI"  # Red
        else:
            prediction = "YRFI"  # Green

        predictions.append({
            "Prediction": prediction,
            "Confidence %": confidence
        })

    result = pd.concat([df.reset_index(drop=True), pd.DataFrame(predictions)], axis=1)
    return result

if __name__ == "__main__":
    df = get_today_games()
    df = calculate_nrfi(df)
    df.to_csv("nrfi_model.csv", index=False)
    print(df)
