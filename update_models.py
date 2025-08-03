import pandas as pd
import numpy as np

TEAM_FILE = "team_nrfi.csv"
PITCHER_FILE = "pitcher_nrfi.csv"

def get_today_games():
    """
    Combines team and pitcher CSVs to simulate today's games.
    Later replace with live ESPN/FanDuel scraping for real matchups.
    """
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    games = []
    for i in range(min(len(teams), len(pitchers))):
        team = teams.iloc[i]
        pitcher = pitchers.iloc[i]

        games.append({
            "Game Time": f"{5+i}:40 PM",  # Placeholder time
            "Matchup": f"{team['Team']} vs Opponent",  # Placeholder opponent
            "Pitchers": pitcher['Pitcher'],
            "Team": team['Team']
        })

    return pd.DataFrame(games)


def calculate_nrfi():
    """
    Calculate NRFI/YRFI % and Confidence Score using team + pitcher stats.
    """

    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    results = []

    for i in range(min(len(teams), len(pitchers))):
        team = teams.iloc[i]
        pitcher = pitchers.iloc[i]

        # Weighted NRFI formula
        team_nrfi = team['NRFI%']
        pitcher_nrfi = pitcher['NRFI%']
        first_inning_era = pitcher['FirstInningERA']

        # Convert ERA into a NRFI factor (lower ERA = higher NRFI chance)
        era_factor = max(0, min(1, 1 - (first_inning_era / 5.0))) * 100

        # Weighted NRFI %
        nrfi_score = round((team_nrfi * 0.4 + pitcher_nrfi * 0.4 + era_factor * 0.2), 1)
        yrfi_score = round(100 - nrfi_score, 1)

        # Confidence is distance from 50%
        confidence = round(abs(nrfi_score - 50), 1)

        # Decide NRFI or YRFI
        prediction = "NRFI" if nrfi_score >= 60 else "YRFI"

        results.append({
            "Game Time": f"{5+i}:40 PM",   # Placeholder time
            "Matchup": f"{team['Team']} vs Opponent",
            "Pitchers": pitcher['Pitcher'],
            "NRFI %": nrfi_score,
            "YRFI %": yrfi_score,
            "Prediction": prediction,
            "Confidence": confidence
        })

    df = pd.DataFrame(results)
    df = df.sort_values(by="Confidence", ascending=False).reset_index(drop=True)
    return df
