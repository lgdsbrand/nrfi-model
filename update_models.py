import pandas as pd
import requests
from datetime import datetime

# ========================
# NRFI / YRFI MODEL
# ========================

def fetch_espn_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    data = requests.get(url).json()
    games = []
    
    for event in data.get("events", []):
        comp = event["competitions"][0]
        game_time = datetime.fromisoformat(comp["date"].replace("Z", "+00:00")).strftime("%I:%M %p ET")
        away_team = comp["competitors"][1]["team"]["displayName"]
        home_team = comp["competitors"][0]["team"]["displayName"]
        
        # Dummy placeholders for real stats (replace with your real data sources)
        away_1st_runs = 0.45
        home_1st_runs_allowed = 0.48
        away_pitcher_nrfi = 0.72
        home_pitcher_nrfi = 0.70
        park_nrfi = 0.55  # e.g., 0.55 = 55% NRFI historically
        
        # Calculate NRFI confidence
        nrfi_prob = (
            (away_pitcher_nrfi * 0.35) +
            (home_pitcher_nrfi * 0.35) +
            ((1 - away_1st_runs) * 0.15) +
            ((1 - home_1st_runs_allowed) * 0.10) +
            (park_nrfi * 0.05)
        )
        
        nrfi_percent = round(nrfi_prob * 100)
        yrfi_percent = 100 - nrfi_percent
        pick = "NRFI" if nrfi_percent >= 50 else "YRFI"

        games.append([
            game_time,
            away_team,
            home_team,
            pick,
            nrfi_percent
        ])
    
    df = pd.DataFrame(games, columns=["Game Time", "Away Team", "Home Team", "Pick", "Confidence"])
    df.to_csv("nrfi_model.csv", index=False)
    print(f"[{datetime.now()}] ✅ NRFI model updated: {len(df)} games.")

if __name__ == "__main__":
    fetch_espn_games()
