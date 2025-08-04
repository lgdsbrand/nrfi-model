import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
CROWDSLINE_URL = "https://www.thecrowdsline.ai/api/nrfi"  # Example endpoint

def get_today_games():
    """
    Scrape ESPN for today's games and starting pitchers
    """
    today = datetime.now().strftime("%Y%m%d")
    resp = requests.get(f"{ESPN_URL}?dates={today}").json()
    games = []

    for event in resp.get("events", []):
        comp = event["competitions"][0]
        home = comp["competitors"][0]
        away = comp["competitors"][1]

        # Extract pitchers if available
        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        # Game time in 12-hour format
        game_time = datetime.fromisoformat(comp["date"][:-1]).strftime("%I:%M %p")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Home Team": home["team"]["displayName"],
            "Away Team": away["team"]["displayName"],
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })

    return pd.DataFrame(games)


def get_crowdsline_data():
    """
    Scrape NRFI/YRFI stats from TheCrowdsLine.
    Example: team NRFI%, pitcher NRFI%, ballpark NRFI%
    """
    try:
        resp = requests.get(CROWDSLINE_URL).json()
        return pd.DataFrame(resp["data"])  # Adjust based on actual JSON
    except:
        return pd.DataFrame()


def calculate_nrfi_predictions():
    """
    Merge ESPN games with NRFI data and calculate prediction/confidence
    """
    games_df = get_today_games()
    crowdsline_df = get_crowdsline_data()

    predictions = []

    for _, row in games_df.iterrows():
        home_pitcher = row["Home Pitcher"]
        away_pitcher = row["Away Pitcher"]

        # Skip if pitcher is TBD
        if "TBD" in home_pitcher or "TBD" in away_pitcher:
            predictions.append({
                "Game Time": row["Game Time"],
                "Matchup": row["Matchup"],
                "Pitchers": row["Pitchers"],
                "Prediction": "",
                "Confidence %": ""
            })
            continue

        # Pull NRFI stats (placeholder logic)
        home_nrfi = 0.55  # 55%
        away_nrfi = 0.60  # 60%
        pitcher_home_nrfi = 0.65
        pitcher_away_nrfi = 0.70
        ballpark_nrfi = 0.50

        # Combine stats for final confidence
        combined_nrfi = (home_nrfi + away_nrfi + pitcher_home_nrfi + pitcher_away_nrfi + ballpark_nrfi) / 5

        if combined_nrfi >= 0.60:
            prediction = "NRFI"
            confidence = round(combined_nrfi * 100, 1)
        else:
            prediction = "YRFI"
            confidence = round((1 - combined_nrfi) * 100, 1)

        predictions.append({
            "Game Time": row["Game Time"],
            "Matchup": row["Matchup"],
            "Pitchers": row["Pitchers"],
            "Prediction": prediction,
            "Confidence %": confidence
        })

    return pd.DataFrame(predictions)


# Run manually for testing
if __name__ == "__main__":
    df = calculate_nrfi_predictions()
    print(df)
