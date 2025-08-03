import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# Load CSV Data
# -----------------------------
team_df = pd.read_csv("team_nrfi.csv")
pitcher_df = pd.read_csv("pitcher_nrfi.csv")

# Normalize names for matching
team_df['Team'] = team_df['Team'].str.strip().str.lower()
pitcher_df['Pitcher'] = pitcher_df['Pitcher'].str.strip()
pitcher_df['Team'] = pitcher_df['Team'].str.strip().str.lower()


# -----------------------------
# Fetch Today's MLB Games
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

        home_team = home["team"]["displayName"]
        away_team = away["team"]["displayName"]

        home_pitcher = home.get("probables", [{}])[0].get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away_team} @ {home_team}",
            "Home Team": home_team,
            "Away Team": away_team,
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })

    return pd.DataFrame(games)


# -----------------------------
# Calculate NRFI/YRFI Confidence
# -----------------------------
def calculate_nrfi(df):
    results = []

    for _, row in df.iterrows():
        home_team = row['Home Team'].strip().lower()
        away_team = row['Away Team'].strip().lower()
        home_pitcher = row['Home Pitcher'].strip()
        away_pitcher = row['Away Pitcher'].strip()

        # Lookup team NRFI%
        home_team_stats = team_df[team_df['Team'] == home_team]
        away_team_stats = team_df[team_df['Team'] == away_team]

        # Lookup pitcher NRFI%
        home_pitcher_stats = pitcher_df[pitcher_df['Pitcher'].str.lower() == home_pitcher.lower()]
        away_pitcher_stats = pitcher_df[pitcher_df['Pitcher'].str.lower() == away_pitcher.lower()]

        # Skip if data is missing
        if home_team_stats.empty or away_team_stats.empty or home_pitcher_stats.empty or away_pitcher_stats.empty:
            continue

        team_nrfi_home = home_team_stats.iloc[0]['NRFI%']
        team_nrfi_away = away_team_stats.iloc[0]['NRFI%']
        pitcher_nrfi_home = home_pitcher_stats.iloc[0]['NRFI%']
        pitcher_nrfi_away = away_pitcher_stats.iloc[0]['NRFI%']

        # Weighted formula (simple average)
        nrfi_pct = round((team_nrfi_home + team_nrfi_away + pitcher_nrfi_home + pitcher_nrfi_away) / 4, 1)

        # Determine NRFI or YRFI & confidence
        if nrfi_pct >= 60:
            prediction = "NRFI"
            confidence = nrfi_pct
        else:
            prediction = "YRFI"
            confidence = round(100 - nrfi_pct, 1)

        results.append({
            "Game Time": row['Game Time'],
            "Matchup": row['Matchup'],
            "Pitchers": row['Pitchers'],
            "NRFI %": nrfi_pct,
            "Prediction": prediction,
            "Confidence %": confidence
        })

    # Create DataFrame & sort by Confidence
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="Confidence %", ascending=False).reset_index(drop=True)

    return results_df
