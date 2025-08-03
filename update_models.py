import pandas as pd
import requests
from datetime import datetime

NRFI_CSV = "nrfi_model.csv"

# === 1. Fetch today's games from ESPN ===
def get_espn_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()

    games = []
    for event in resp.get("events", []):
        comp = event["competitions"][0]
        teams = comp["competitors"]
        home = next(t["team"]["displayName"] for t in teams if t["homeAway"] == "home")
        away = next(t["team"]["displayName"] for t in teams if t["homeAway"] == "away")
        game_time = datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ").strftime("%I:%M %p ET")

        games.append({
            "game_time": game_time,
            "home_team": home,
            "away_team": away
        })

    return pd.DataFrame(games)

# === 2. Fetch stats from TheCrowdsLine (replace with real API or scrape) ===
def get_crowdsline_stats(home_team, away_team):
    # Example structure — replace with real scraped or API data
    return {
        "home_pitcher_nrfi": 0.78,
        "away_pitcher_nrfi": 0.82,
        "home_team_nrfi": 0.70,
        "away_team_nrfi": 0.68,
        "ballpark_nrfi": 0.65,
        "home_first_inning_era": 1.40,
        "away_first_inning_era": 1.30,
        "home_first_inning_rpg": 0.55,
        "away_first_inning_rpg": 0.50
    }

# === 3. NRFI calculation formula ===
def calculate_nrfi(row):
    stats = get_crowdsline_stats(row["home_team"], row["away_team"])

    # Factor 1: Pitchers NRFI %
    pitcher_avg = (stats["home_pitcher_nrfi"] + stats["away_pitcher_nrfi"]) / 2

    # Factor 2: Team NRFI %
    team_avg = (stats["home_team_nrfi"] + stats["away_team_nrfi"]) / 2

    # Factor 3: Ballpark NRFI %
    ballpark = stats["ballpark_nrfi"]

    # Factor 4: First Inning ERA & Runs
    first_inning_factor = (
        (2 - (stats["home_first_inning_era"] + stats["away_first_inning_era"]) / 2) +
        (1 - (stats["home_first_inning_rpg"] + stats["away_first_inning_rpg"]) / 2)
    ) / 2

    # Combined NRFI Confidence Score
    nrfi_score = (pitcher_avg * 0.35) + (team_avg * 0.25) + (ballpark * 0.15) + (first_inning_factor * 0.25)
    nrfi_confidence = round(nrfi_score * 100)

    # Determine pick
    pick = "NRFI" if nrfi_confidence >= 50 else "YRFI"
    return pd.Series([pick, nrfi_confidence], index=["Pick", "Confidence"])

# === 4. Generate & save model ===
def generate_nrfi_model():
    df = get_espn_games()
    df[["Pick", "Confidence"]] = df.apply(calculate_nrfi, axis=1)
    df.to_csv(NRFI_CSV, index=False)
    print(f"✅ NRFI model updated at {datetime.now()}")

if __name__ == "__main__":
    generate_nrfi_model()
