import pandas as pd
import requests
from datetime import datetime

# === Helper: Calculate NRFI/YRFI confidence ===
def calculate_nrfi_confidence(away_team, home_team, away_pitcher, home_pitcher, ballpark_factor=1.0):
    """
    Combine multiple stats to compute NRFI confidence.
    Formula (example weighting):
      35% Starting Pitcher NRFI rate
      25% Team 1st Inning Scoring/Allowed
      20% Opponent NRFI rate
      20% Ballpark factor (lower favors NRFI)
    """

    # Dummy stats for example (replace with actual API calls later)
    away_team_nrfi = 0.55  # Team NRFI rate (away)
    home_team_nrfi = 0.52  # Team NRFI rate (home)
    away_pitcher_nrfi = 0.60  # Pitcher's NRFI rate
    home_pitcher_nrfi = 0.62

    # Combined probability for no runs first inning
    nrfi_prob = (
        (away_pitcher_nrfi + home_pitcher_nrfi) * 0.35 +
        (away_team_nrfi + home_team_nrfi) * 0.25 +
        ((1-away_team_nrfi) + (1-home_team_nrfi)) * 0.20 +
        (ballpark_factor * 0.20)
    ) / 2  # normalize

    nrfi_conf = int(round(nrfi_prob * 100, 0))
    yrfi_conf = 100 - nrfi_conf

    pick = "NRFI" if nrfi_conf >= yrfi_conf else "YRFI"
    return pick, nrfi_conf

# === Main function: Pull games & calculate NRFI ===
def generate_nrfi_model():
    today = datetime.now().strftime("%Y%m%d")
    espn_url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    data = requests.get(espn_url).json()

    games = []
    for event in data.get("events", []):
        game_time = datetime.fromisoformat(event["date"][:-1]).strftime("%I:%M %p ET")
        away_team = event["competitions"][0]["competitors"][1]["team"]["displayName"]
        home_team = event["competitions"][0]["competitors"][0]["team"]["displayName"]

        # Pull pitchers if available
        away_pitcher = event["competitions"][0]["competitors"][1].get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        home_pitcher = event["competitions"][0]["competitors"][0].get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        pick, conf = calculate_nrfi_confidence(away_team, home_team, away_pitcher, home_pitcher)

        games.append([game_time, away_team, home_team, pick, conf])

    columns = ["Game Time", "Away Team", "Home Team", "Pick", "Confidence"]
    df = pd.DataFrame(games, columns=columns)
    df.to_csv("nrfi_model.csv", index=False)
    return df

if __name__ == "__main__":
    df = generate_nrfi_model()
    print(f"✅ NRFI Model Updated at {datetime.now()} with {len(df)} games.")
