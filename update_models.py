import requests
import pandas as pd
from datetime import datetime

# === CONFIG ===
CSV_FILENAME = "nrfi_model.csv"

# Helper: Convert time to EST in 12-hour format
def convert_game_time(utc_time):
    dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%MZ")
    return dt.strftime("%I:%M %p")

# Fetch today's MLB games from ESPN
def get_espn_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()
    games = []
    for event in resp.get("events", []):
        game_time = convert_game_time(event["date"])
        teams = event["competitions"][0]["competitors"]
        home_team = next(t for t in teams if t["homeAway"] == "home")["team"]["displayName"]
        away_team = next(t for t in teams if t["homeAway"] == "away")["team"]["displayName"]
        games.append({
            "game_time": game_time,
            "home_team": home_team,
            "away_team": away_team
        })
    return pd.DataFrame(games)

# Fetch NRFI stats from TheCrowdsLine.ai (sample / placeholder API call)
def get_crowdsline_nrfi_data():
    # In production, replace with actual scraping or API call to TheCrowdsLine.ai
    # Expect columns: home_pitcher_nrfi, away_pitcher_nrfi, home_team_nrfi, away_team_nrfi,
    # home_pitcher_1st_era, away_pitcher_1st_era, ballpark_nrfi
    return pd.DataFrame([
        # Example: This will be replaced with real data fetching
        {
            "home_team": "Detroit Tigers",
            "away_team": "Philadelphia Phillies",
            "home_pitcher_nrfi": 0.82,
            "away_pitcher_nrfi": 0.81,
            "home_team_nrfi": 0.70,
            "away_team_nrfi": 0.72,
            "home_pitcher_1st_era": 1.20,
            "away_pitcher_1st_era": 1.10,
            "ballpark_nrfi": 0.68
        },
    ])

# Calculate NRFI/YRFI confidence
def calculate_nrfi_conf(row):
    avg_pitcher_nrfi = (row["home_pitcher_nrfi"] + row["away_pitcher_nrfi"]) / 2
    avg_team_nrfi = (row["home_team_nrfi"] + row["away_team_nrfi"]) / 2
    ballpark_factor = row["ballpark_nrfi"]
    era_factor = 1 - ((row["home_pitcher_1st_era"] + row["away_pitcher_1st_era"]) / 2) / 9

    # Final confidence
    nrfi_conf = avg_pitcher_nrfi * avg_team_nrfi * ballpark_factor * era_factor * 100

    pick = "NRFI" if nrfi_conf >= 50 else "YRFI"
    confidence = max(nrfi_conf, 100 - nrfi_conf)

    return pd.Series([pick, round(confidence)])

def main():
    games_df = get_espn_games()
    nrfi_data = get_crowdsline_nrfi_data()

    df = pd.merge(games_df, nrfi_data, on=["home_team", "away_team"], how="left")

    df[["Pick", "Confidence"]] = df.apply(calculate_nrfi_conf, axis=1)

    output_df = df[["game_time", "away_team", "home_team", "Pick", "Confidence"]]
    output_df.to_csv(CSV_FILENAME, index=False)
    print(f"NRFI model updated: {CSV_FILENAME}")

if __name__ == "__main__":
    main()
