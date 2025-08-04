import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
CROWDSLINE_URL = "https://www.thecrowdsline.ai/api/mlb/nrfi"  # Example endpoint

def get_today_games():
    """Scrape ESPN for today’s games and starting pitchers"""
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
            "Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Home Team": home["team"]["displayName"],
            "Away Team": away["team"]["displayName"],
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })

    return pd.DataFrame(games)


def get_crowdsline_data():
    """Scrape TheCrowdsLine.ai for NRFI/YRFI data"""
    resp = requests.get(CROWDSLINE_URL).json()
    data = []

    for g in resp.get("games", []):
        data.append({
            "Home Team": g["homeTeam"],
            "Away Team": g["awayTeam"],
            "Home Pitcher": g["homePitcher"],
            "Away Pitcher": g["awayPitcher"],
            "Home NRFI%": g.get("homeNRFI", 50),
            "Away NRFI%": g.get("awayNRFI", 50),
            "Home 1st ERA": g.get("homeERA", 4.0),
            "Away 1st ERA": g.get("awayERA", 4.0),
            "Ballpark NRFI%": g.get("ballparkNRFI", 50)
        })

    return pd.DataFrame(data)


def calculate_nrfi_predictions():
    """Combine ESPN schedule with TheCrowdsLine data and calculate NRFI/YRFI"""
    games = get_today_games()
    cl_data = get_crowdsline_data()

    merged = games.merge(cl_data, how="left", 
                         on=["Home Team", "Away Team", "Home Pitcher", "Away Pitcher"])

    results = []
    for _, row in merged.iterrows():
        if "TBD" in row["Pitchers"]:
            # Skip predictions if TBD
            prediction, confidence = "", ""
        else:
            confidence = (
                row["Home NRFI%"] + row["Away NRFI%"] + row["Ballpark NRFI%"]
            ) / 3  # Simple avg for now

            prediction = "NRFI" if confidence >= 60 else "YRFI"

        results.append({
            "Game Time": row["Time"],
            "Matchup": row["Matchup"],
            "Pitchers": row["Pitchers"],
            "Prediction": prediction,
            "Confidence %": confidence
        })

    df = pd.DataFrame(results)
    df.to_csv("nrfi_model.csv", index=False)
    return df
