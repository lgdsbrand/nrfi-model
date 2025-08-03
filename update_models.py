import pandas as pd
import requests
from datetime import datetime

def run_nrfi_model():
    # -----------------------------
    # Scrape today's MLB schedule
    # -----------------------------
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()

    # Load your team & pitcher NRFI data
    team_df = pd.read_csv("team_nrfi.csv")
    pitcher_df = pd.read_csv("pitcher_nrfi.csv")

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

        # Get team NRFI %
        team_home = team_df.loc[team_df["Team"] == home_team, "NRFI%"].values
        team_away = team_df.loc[team_df["Team"] == away_team, "NRFI%"].values
        team_home_nrfi = team_home[0] if len(team_home) else 65
        team_away_nrfi = team_away[0] if len(team_away) else 65

        # Get pitcher NRFI %
        pitcher_home = pitcher_df.loc[pitcher_df["Pitcher"] == home_pitcher, "NRFI%"].values
        pitcher_away = pitcher_df.loc[pitcher_df["Pitcher"] == away_pitcher, "NRFI%"].values
        pitcher_home_nrfi = pitcher_home[0] if len(pitcher_home) else 65
        pitcher_away_nrfi = pitcher_away[0] if len(pitcher_away) else 65

        # Weighted formula (simple avg of teams & pitchers)
        nrfi_pct = round(
            (team_home_nrfi + team_away_nrfi + pitcher_home_nrfi + pitcher_away_nrfi) / 4, 1
        )

        # Determine confidence label (NRFI or YRFI)
        if nrfi_pct >= 60:
            label = "NRFI"
            confidence = nrfi_pct
        else:
            label = "YRFI"
            confidence = 100 - nrfi_pct

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away_team} @ {home_team}",
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "NRFI/YRFI": label,
            "Confidence %": confidence
        })

    df = pd.DataFrame(games)

    # Sort by Confidence %
    df = df.sort_values(by="Confidence %", ascending=False).reset_index(drop=True)

    # Save CSV
    df.to_csv("nrfi_model.csv", index=False)
    return df
