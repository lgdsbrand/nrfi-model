import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

CSV_FILENAME = "nrfi_model.csv"

# === 1. Pull today's games from ESPN ===
def get_espn_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()

    games = []
    for event in resp.get("events", []):
        comp = event["competitions"][0]
        teams = comp["competitors"]
        home = next(t["team"]["displayName"] for t in teams if t["homeAway"] == "home")
        away = next(t["team"]["displayName"] for t in teams if t["homeAway"] == "away")

        game_time = datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ")
        game_time_str = game_time.strftime("%I:%M %p ET")

        games.append({
            "game_time": game_time_str,
            "home_team": home,
            "away_team": away
        })

    return pd.DataFrame(games)


# === 2. Scrape NRFI Stats from TheCrowdsLine.ai ===
def get_crowdsline_stats(team, pitcher):
    """
    Scrapes TheCrowdsLine.ai for NRFI data.
    Assumes pages have consistent team & pitcher tables.
    """
    # Format team name for URL if needed (example placeholder)
    team_slug = team.replace(" ", "-").lower()
    url = f"https://www.thecrowdsline.ai/mlb/nrfi/{team_slug}"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # --- Example parsing (you will adjust selectors if needed) ---
    # Look for NRFI% table
    pitcher_nrfi = 0.75
    team_nrfi = 0.70
    ballpark_nrfi = 0.68
    first_inning_era = 1.55
    first_inning_rpg = 0.55
    first_inning_rpga = 0.52

    return {
        "pitcher_nrfi": pitcher_nrfi,
        "team_nrfi": team_nrfi,
        "ballpark_nrfi": ballpark_nrfi,
        "first_inning_era": first_inning_era,
        "first_inning_rpg": first_inning_rpg,
        "first_inning_rpga": first_inning_rpga
    }


# === 3. Calculate NRFI Confidence ===
def calculate_nrfi(home_stats, away_stats):
    # Average NRFI metrics from home & away pitchers and teams
    avg_pitcher_nrfi = (home_stats["pitcher_nrfi"] + away_stats["pitcher_nrfi"]) / 2
    avg_team_nrfi = (home_stats["team_nrfi"] + away_stats["team_nrfi"]) / 2
    avg_ballpark_nrfi = (home_stats["ballpark_nrfi"] + away_stats["ballpark_nrfi"]) / 2

    # Combine stats into confidence score
    confidence = (
        avg_pitcher_nrfi * 0.4 +
        avg_team_nrfi * 0.3 +
        avg_ballpark_nrfi * 0.2 +
        (1 - ((home_stats["first_inning_era"] + away_stats["first_inning_era"]) / 2) / 5.0) * 0.1
    )

    confidence_pct = round(confidence * 100, 0)
    pick = "NRFI" if confidence_pct >= 50 else "YRFI"

    return pick, confidence_pct


# === 4. Main function to generate NRFI model ===
def generate_nrfi_model():
    games_df = get_espn_games()
    records = []

    for _, row in games_df.iterrows():
        home_stats = get_crowdsline_stats(row["home_team"], "HomePitcher")
        away_stats = get_crowdsline_stats(row["away_team"], "AwayPitcher")
        pick, confidence = calculate_nrfi(home_stats, away_stats)

        records.append([
            row["game_time"], row["away_team"], row["home_team"], pick, confidence
        ])

    df = pd.DataFrame(records, columns=["Game Time", "Away Team", "Home Team", "Pick", "Confidence"])
    df.to_csv(CSV_FILENAME, index=False)
    return df


if __name__ == "__main__":
    df = generate_nrfi_model()
    print("✅ NRFI model updated:", df)
