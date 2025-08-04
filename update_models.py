import pandas as pd
import numpy as np
import requests
from datetime import datetime

# -----------------------------
# ESPN API for MLB Schedule
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

        # Starting pitchers (fallback to TBD if not listed)
        home_pitcher = home.get("probables", [{}])[0].get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Home Team": home['team']['displayName'],
            "Away Team": away['team']['displayName'],
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })
    return pd.DataFrame(games)

# -----------------------------
# NRFI/YRFI Model Formula
# -----------------------------
def calculate_nrfi(df):
    predictions = []

    for _, row in df.iterrows():
        # Skip prediction if pitcher is TBD
        if "TBD" in row["Pitchers"]:
            predictions.append({"Prediction": "", "Confidence %": ""})
            continue

        # Example formula: combine team & pitcher NRFI %
        # Placeholder values – replace with TheCrowdsLine + TeamRankings scrape
        team_nrfi_home = np.random.randint(55, 80)
        team_nrfi_away = np.random.randint(55, 80)
        pitcher_nrfi_home = np.random.randint(50, 85)
        pitcher_nrfi_away = np.random.randint(50, 85)

        # Weighted average formula
        confidence = round(
            (team_nrfi_home + team_nrfi_away + pitcher_nrfi_home + pitcher_nrfi_away) / 4, 1
        )

        # Determine NRFI vs YRFI
        prediction = "NRFI" if confidence >= 60 else "YRFI"

        predictions.append({
            "Prediction": prediction,
            "Confidence %": confidence
        })

    return pd.DataFrame(predictions)

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    games_df = get_today_games()
    predictions_df = calculate_nrfi(games_df)

    final_df = pd.concat([games_df[["Game Time", "Matchup", "Pitchers"]], predictions_df], axis=1)

    # Save for Streamlit app
    final_df.to_csv("nrfi_model.csv", index=False)
    print("NRFI model updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
