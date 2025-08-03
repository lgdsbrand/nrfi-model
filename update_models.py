import pandas as pd
import numpy as np

TEAM_FILE = "team_nrfi.csv"
PITCHER_FILE = "pitcher_nrfi.csv"

def get_today_games():
    """
    Combines team and pitcher CSV data to simulate today's matchups.
    Returns a list of dictionaries for NRFI/YRFI calculations.
    """
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    games = []
    for i in range(min(len(teams), len(pitchers), len(pitchers)-1)):
        home_team = teams.iloc[i % len(teams)]
        away_team = teams.iloc[(i+1) % len(teams)]

        home_pitcher = pitchers.iloc[i % len(pitchers)]
        away_pitcher = pitchers.iloc[(i+1) % len(pitchers)]

        games.append({
            "Game Time": f"{3+i}:05 PM",
            "Matchup": f"{away_team['Team']} @ {home_team['Team']}",
            "Pitchers": f"{away_pitcher['Pitcher']} vs {home_pitcher['Pitcher']}",
            "home_team": home_team['Team'],
            "away_team": away_team['Team'],
            "home_pitcher": home_pitcher['Pitcher'],
            "away_pitcher": away_pitcher['Pitcher']
        })

    return games


def calculate_nrfi(games):
    """
    Calculates NRFI/YRFI % and confidence for each game.
    """
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    results = []
    for game in games:
        home_team_stats = teams[teams['Team'] == game['home_team']].iloc[0]
        away_team_stats = teams[teams['Team'] == game['away_team']].iloc[0]

        home_pitcher_stats = pitchers[pitchers['Pitcher'] == game['home_pitcher']].iloc[0]
        away_pitcher_stats = pitchers[pitchers['Pitcher'] == game['away_pitcher']].iloc[0]

        # NRFI Score Calculation
        team_factor = (home_team_stats['NRFI%'] + away_team_stats['NRFI%']) / 2
        pitcher_factor = (home_pitcher_stats['NRFI%'] + away_pitcher_stats['NRFI%']) / 2
        era_factor = max(0, 100 - ((home_pitcher_stats['FirstInningERA'] + 
                                   away_pitcher_stats['FirstInningERA']) * 10))

        nrfi_score = round((team_factor * 0.4 + pitcher_factor * 0.4 + era_factor * 0.2), 1)
        yrfi_score = round(100 - nrfi_score, 1)

        # Confidence Score
        confidence = nrfi_score if nrfi_score >= 50 else yrfi_score

        # Label NRFI or YRFI
        prediction = "NRFI" if nrfi_score >= 50 else "YRFI"

        results.append({
            "Game Time": game['Game Time'],
            "Matchup": game['Matchup'],
            "Pitchers": game['Pitchers'],
            "Prediction": prediction,
            "NRFI %": nrfi_score,
            "YRFI %": yrfi_score,
            "Confidence": confidence
        })

    return pd.DataFrame(results)
