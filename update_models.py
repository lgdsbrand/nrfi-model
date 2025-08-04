import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
CROWDSLINE_TEAM_URL = "https://www.thecrowdsline.ai/mlb/team-nrfi"  # Placeholder
CROWDSLINE_PITCHER_URL = "https://www.thecrowdsline.ai/mlb/pitcher-nrfi"  # Placeholder
CROWDSLINE_BALLPARK_URL = "https://www.thecrowdsline.ai/mlb/ballpark-nrfi"  # Placeholder

# -----------------------------
# 1. SCRAPE TODAY'S GAMES
# -----------------------------
def get_today_games():
    today = datetime.now().strftime("%Y%m%d")
    resp = requests.get(f"{ESPN_URL}?dates={today}").json()

    games = []
    for event in resp.get("events", []):
        comp = event["competitions"][0]
        home = comp["competitors"][0]
        away = comp["competitors"][1]

        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD") if home.get("probables") else "TBD"
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD") if away.get("probables") else "TBD"

        game_time = datetime.fromisoformat(comp["date"][:-1]).strftime("%I:%M %p")

        games.append({
            "Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Home Team": home["team"]["displayName"],
            "Away Team": away["team"]["displayName"],
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })

    return pd.DataFrame(games)

# -----------------------------
# 2. SCRAPE CROWDSLINE DATA (SIMULATED)
# -----------------------------
def scrape_crowdsline_data():
    """
    In production: scrape TheCrowdsLine or use API.
    For now, returns simulated NRFI% & Ballpark NRFI%.
    """
    # Example data to simulate
    return {
        "team_nrfi": {
            "Houston Astros": 62,
            "Miami Marlins": 58,
            "Minnesota Twins": 60,
            "Detroit Tigers": 55
        },
        "pitcher_nrfi": {
            "Sandy Alcantara": 72,
            "Jason Alexander": 60,
            "Casey Mize": 65,
            "Simeon Woods Richardson": 55
        },
        "ballpark_nrfi": {
            "loanDepot Park": 65,
            "Target Field": 58
        }
    }

# -----------------------------
# 3. CALCULATE NRFI/YRFI PREDICTIONS
# -----------------------------
def calculate_nrfi_predictions():
    games_df = get_today_games()
    crowds_data = scrape_crowdsline_data()

    predictions = []
    for _, row in games_df.iterrows():
        away_pitcher = row["Away Pitcher"]
        home_pitcher = row["Home Pitcher"]
        home_team = row["Home Team"]
        away_team = row["Away Team"]

        # If TBD, leave prediction blank
        if "TBD" in away_pitcher or "TBD" in home_pitcher:
            predictions.append({"Prediction": "", "Confidence %": ""})
            continue

        # Pull stats (fallback to 50% if missing)
        home_nrfi = crowds_data["team_nrfi"].get(home_team, 50)
        away_nrfi = crowds_data["team_nrfi"].get(away_team, 50)
        home_pitcher_nrfi = crowds_data["pitcher_nrfi"].get(home_pitcher, 50)
        away_pitcher_nrfi = crowds_data["pitcher_nrfi"].get(away_pitcher, 50)
        ballpark_nrfi = 60  # Default, could scrape stadium name mapping

        # Combine into a confidence score
        confidence = (home_nrfi + away_nrfi + home_pitcher_nrfi + away_pitcher_nrfi + ballpark_nrfi) / 5

        # Determine prediction
        if confidence >= 60:
            prediction = "NRFI"
        else:
            prediction = "YRFI"

        predictions.append({
            "Prediction": prediction,
            "Confidence %": round(confidence, 1)
        })

    # Merge predictions into games_df
    pred_df = pd.DataFrame(predictions)
    final_df = pd.concat([games_df, pred_df], axis=1)
    return final_df

if __name__ == "__main__":
    df = calculate_nrfi_predictions()
    df.to_csv("nrfi_model.csv", index=False)
