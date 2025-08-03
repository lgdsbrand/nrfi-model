import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# Load CSVs with real stats
# -----------------------------
team_df = pd.read_csv("team_nrfi.csv")        # Columns: Team, NRFI%
pitcher_df = pd.read_csv("pitcher_nrfi.csv")  # Columns: Pitcher, NRFI%, FirstInningERA
park_factors = pd.read_csv("ballpark_factors.csv")  # Optional: Ballpark, Factor

# -----------------------------
# Fetch today's games from ESPN
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

        # Grab starting pitchers
        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away_team} @ {home_team}",
            "Home Team": home_team,
            "Away Team": away_team,
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })

    return pd.DataFrame(games)

# -----------------------------
# Compute NRFI/YRFI Score
# -----------------------------
def calculate_nrfi(df):
    results = []
    for _, row in df.iterrows():
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        home_pitcher = row["Home Pitcher"]
        away_pitcher = row["Away Pitcher"]

        # Lookup stats (fallback to 50 if not found)
        team_home_nrfi = team_df.loc[team_df["Team"] == home_team, "NRFI%"].max() if home_team in team_df["Team"].values else 50
        team_away_nrfi = team_df.loc[team_df["Team"] == away_team, "NRFI%"].max() if away_team in team_df["Team"].values else 50

        pitcher_home_nrfi = pitcher_df.loc[pitcher_df["Pitcher"] == home_pitcher, "NRFI%"].max() if home_pitcher in pitcher_df["Pitcher"].values else 50
        pitcher_away_nrfi = pitcher_df.loc[pitcher_df["Pitcher"] == away_pitcher, "NRFI%"].max() if away_pitcher in pitcher_df["Pitcher"].values else 50

        # Ballpark factor (0 = neutral)
        park_factor = park_factors.loc[park_factors["Ballpark"] == row["Matchup"].split(" @ ")[1], "Factor"].max() if row["Matchup"].split(" @ ")[1] in park_factors["Ballpark"].values else 0

        # Weighted NRFI Score (simple average + ballpark tweak)
        nrfi_score = (
            team_home_nrfi * 0.25 +
            team_away_nrfi * 0.25 +
            pitcher_home_nrfi * 0.25 +
            pitcher_away_nrfi * 0.25
        ) + park_factor

        nrfi_score = max(0, min(100, nrfi_score))  # Clamp 0-100

        # Determine NRFI or YRFI
        if nrfi_score >= 60:
            prediction = "NRFI"
            confidence = nrfi_score
        else:
            prediction = "YRFI"
            confidence = 100 - nrfi_score

        results.append({
            "Game Time": row["Game Time"],
            "Matchup": row["Matchup"],
            "Pitchers": f"{row['Away Pitcher']} vs {row['Home Pitcher']}",
            "Prediction": prediction,
            "Confidence %": round(confidence, 1)
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="Confidence %", ascending=False).reset_index(drop=True)
    return results_df

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    games_df = get_today_games()
    final_df = calculate_nrfi(games_df)
    final_df.to_csv("nrfi_model.csv", index=False)
    print(final_df)
