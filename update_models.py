import requests
import pandas as pd
from datetime import datetime

# Load real stats from CSVs
team_stats = pd.read_csv("team_nrfi.csv")
pitcher_stats = pd.read_csv("pitcher_nrfi.csv")

def fetch_weather_factor(event):
    """Returns a weather/ballpark factor for NRFI %"""
    comp = event["competitions"][0]
    venue = comp.get("venue", {})
    weather = comp.get("weather", {})

    # Default neutral
    factor = 0

    # Dome boost
    if "indoor" in venue.get("fullName", "").lower() or venue.get("indoor", False):
        return 0.05

    # Weather adjustments
    wind_speed = weather.get("windSpeed", 0)
    condition = weather.get("condition", "").lower()

    if wind_speed and "out" in condition:
        factor -= 0.05
    if "rain" in condition or "shower" in condition:
        factor -= 0.05

    return factor

def pitcher_era_factor(era):
    """Converts 1st inning ERA into NRFI confidence adjustment"""
    if era <= 2.0:
        return 0.10
    elif era <= 3.5:
        return 0.0
    else:
        return -0.10

def run_nrfi_model():
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

        home_pitcher = home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD")

        # Get real stats from CSVs
        home_team_stats = team_stats[team_stats["Team"] == home_team].iloc[0]
        away_team_stats = team_stats[team_stats["Team"] == away_team].iloc[0]

        home_pitcher_stats = pitcher_stats[pitcher_stats["Pitcher"] == home_pitcher].iloc[0]
        away_pitcher_stats = pitcher_stats[pitcher_stats["Pitcher"] == away_pitcher].iloc[0]

        # Weighted NRFI formula
        team_component = (home_team_stats["NRFI%"] + away_team_stats["NRFI%"]) / 2 * 0.25
        pitcher_component = (home_pitcher_stats["NRFI%"] + away_pitcher_stats["NRFI%"]) / 2 * 0.35
        era_component = (
            pitcher_era_factor(home_pitcher_stats["FirstInningERA"]) +
            pitcher_era_factor(away_pitcher_stats["FirstInningERA"])
        ) / 2 * 100 * 0.15
        weather_component = fetch_weather_factor(event) * 100 * 0.10

        nrfi_pct = round(team_component + pitcher_component + era_component + weather_component, 1)
        nrfi_pct = max(min(nrfi_pct, 99), 1)

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away_team} @ {home_team}",
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "NRFI %": nrfi_pct
        })

    df = pd.DataFrame(games)
    df = df.sort_values(by="NRFI %", ascending=False).reset_index(drop=True)
    return df
