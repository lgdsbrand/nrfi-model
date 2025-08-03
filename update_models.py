import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# Helper: Fetch Today's Games
# -----------------------------
def get_today_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()

    games = []
    for event in resp.get("events", []):
        comp = event["competitions"][0]
        home = comp["competitors"][0]
        away = comp["competitors"][1]

        game_time = datetime.fromisoformat(comp["date"][:-1]).strftime("%I:%M %p")

        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Home Team": home['team']['displayName'],
            "Away Team": away['team']['displayName'],
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })
    return pd.DataFrame(games)

# -----------------------------
# Helper: Fake NRFI/YRFI Stats
# Replace these with TheCrowdsLine/TeamRankings in production
# -----------------------------
def get_team_pitcher_stats(team, pitcher):
    # Simulated fallback stats (real integration would scrape)
    team_stats = {
        "Yankees": {"team_nrfi": 63, "team_yrfi": 37},
        "Red Sox": {"team_nrfi": 58, "team_yrfi": 42},
        "Dodgers": {"team_nrfi": 70, "team_yrfi": 30},
        "Giants": {"team_nrfi": 65, "team_yrfi": 35},
    }
    pitcher_stats = {
        "Gerrit Cole": {"pitcher_nrfi": 78, "era_1st": 1.20},
        "Brayan Bello": {"pitcher_nrfi": 65, "era_1st": 2.10},
        "Walker Buehler": {"pitcher_nrfi": 82, "era_1st": 0.95},
        "Logan Webb": {"pitcher_nrfi": 70, "era_1st": 1.45},
    }

    team_info = team_stats.get(team, {"team_nrfi": 60, "team_yrfi": 40})
    pitcher_info = pitcher_stats.get(pitcher, {"pitcher_nrfi": 60, "era_1st": 2.00})
    return team_info, pitcher_info

# -----------------------------
# Calculate NRFI/YRFI Confidence
# -----------------------------
def calculate_nrfi(df):
    results = []
    for _, row in df.iterrows():
        home_pitcher = row["Home Pitcher"]
        away_pitcher = row["Away Pitcher"]

        # Skip if TBD pitcher
        if "TBD" in home_pitcher or "TBD" in away_pitcher:
            results.append({**row, "Prediction": "", "Confidence %": ""})
            continue

        # Get team & pitcher stats
        home_team_stats, home_pitcher_stats = get_team_pitcher_stats(row["Home Team"], home_pitcher)
        away_team_stats, away_pitcher_stats = get_team_pitcher_stats(row["Away Team"], away_pitcher)

        # Weighted NRFI confidence calculation
        team_conf = (home_team_stats["team_nrfi"] + away_team_stats["team_nrfi"]) / 2
        pitcher_conf = (home_pitcher_stats["pitcher_nrfi"] + away_pitcher_stats["pitcher_nrfi"]) / 2

        # ERA penalty: lower ERA increases NRFI confidence, cap +/- 5%
        era_factor = max(0, 3 - (home_pitcher_stats["era_1st"] + away_pitcher_stats["era_1st"]) / 2) * 5
        confidence = round((team_conf * 0.4) + (pitcher_conf * 0.4) + era_factor, 1)

        prediction = "NRFI" if confidence >= 60 else "YRFI"

        results.append({**row, "Prediction": prediction, "Confidence %": confidence})

    return pd.DataFrame(results)[["Game Time", "Matchup", "Home Pitcher", "Away Pitcher", "Prediction", "Confidence %"]]
