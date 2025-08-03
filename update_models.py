import requests
import pandas as pd
from datetime import datetime

def run_nrfi_model():
    """
    Scrapes today's MLB games and calculates NRFI % predictions
    using team and pitcher 1st inning data with simple weighting.
    """

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

        # Pitchers
        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        # -------------------------
        # NRFI formula logic
        # -------------------------
        # These are placeholders for real data sources:
        # - Team NRFI% (would pull from TeamRankings or your database)
        # - Pitcher 1st inning ERA / NRFI%
        # Here we simulate a weighted formula for demonstration.

        import random
        team_nrfi_home = random.randint(55, 80)
        team_nrfi_away = random.randint(55, 80)
        pitcher_nrfi_home = random.randint(50, 85)
        pitcher_nrfi_away = random.randint(50, 85)
        park_factor = random.randint(-5, 5)  # negative boosts NRFI

        nrfi_pct = round(
            (team_nrfi_home + team_nrfi_away) / 2 * 0.4
            + (pitcher_nrfi_home + pitcher_nrfi_away) / 2 * 0.5
            + park_factor,
            1
        )

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away_team} @ {home_team}",
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "NRFI %": max(min(nrfi_pct, 99), 1)  # keep within 1-99%
        })

    df = pd.DataFrame(games)
    df = df.sort_values(by="NRFI %", ascending=False).reset_index(drop=True)
    return df
