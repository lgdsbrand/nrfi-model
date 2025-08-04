import pandas as pd
import requests
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
CROWDSLINE_URL = "https://www.thecrowdsline.ai/api/nrfi"  # Example placeholder
OUTPUT_CSV = "nrfi_model.csv"


def get_today_games():
    """Scrape ESPN for today's games and starting pitchers"""
    today = datetime.now().strftime("%Y%m%d")
    resp = requests.get(f"{ESPN_URL}?dates={today}").json()
    games = []

    for event in resp.get("events", []):
        comp = event["competitions"][0]
        home = comp["competitors"][0]
        away = comp["competitors"][1]

        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        game_time = datetime.fromisoformat(comp["date"][:-1]).strftime("%I:%M %p")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Home Team": home['team']['displayName'],
            "Away Team": away['team']['displayName'],
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher,
            "Pitchers": f"{away_pitcher} vs {home_pitcher}"
        })

    return pd.DataFrame(games)


def get_crowdsline_data():
    """Scrape TheCrowdsLine for NRFI/YRFI data (placeholder)"""
    try:
        resp = requests.get(CROWDSLINE_URL).json()
        df = pd.DataFrame(resp["data"])  # Adjust to actual JSON structure
        # Expect columns: Team, NRFI%, YRFI%, Ballpark_NRFI%, FirstInningERA
        return df
    except:
        return pd.DataFrame(columns=["Team", "NRFI%", "YRFI%", "Ballpark_NRFI%", "FirstInningERA"])


def calculate_confidence(row, team_data):
    """Calculate NRFI/YRFI confidence based on team + pitcher + ballpark"""
    if "TBD" in row["Home Pitcher"] or "TBD" in row["Away Pitcher"]:
        return "", ""

    home = team_data[team_data["Team"] == row["Home Team"]]
    away = team_data[team_data["Team"] == row["Away Team"]]

    if home.empty or away.empty:
        return "", ""

    # Weighted confidence calculation
    home_nrfi = float(home["NRFI%"].values[0])
    away_nrfi = float(away["NRFI%"].values[0])
    ballpark = float(home["Ballpark_NRFI%"].values[0])

    avg_nrfi = (home_nrfi + away_nrfi + ballpark) / 3

    prediction = "NRFI" if avg_nrfi >= 60 else "YRFI"  # Threshold adjusted
    confidence = round(avg_nrfi, 1)

    return prediction, confidence


def calculate_nrfi_predictions():
    """Generate full NRFI/YRFI predictions table"""
    games_df = get_today_games()
    team_data = get_crowdsline_data()

    predictions = []
    for _, row in games_df.iterrows():
        prediction, confidence = calculate_confidence(row, team_data)
        predictions.append({
            "Game Time": row["Game Time"],
            "Matchup": row["Matchup"],
            "Pitchers": row["Pitchers"],
            "Prediction": prediction,
            "Confidence %": confidence
        })

    final_df = pd.DataFrame(predictions)
    final_df.to_csv(OUTPUT_CSV, index=False)
    return final_df


# If run manually, generate today's file
if __name__ == "__main__":
    df = calculate_nrfi_predictions()
    print(df)
