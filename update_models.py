import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# -------------------------
# 1. Fetch MLB Schedule
# -------------------------
def fetch_mlb_schedule():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    data = requests.get(url).json()

    games = []
    for event in data.get("events", []):
        game_time = datetime.fromisoformat(event["date"][:-1]).strftime("%I:%M %p ET")
        away_team = event["competitions"][0]["competitors"][1]["team"]["displayName"]
        home_team = event["competitions"][0]["competitors"][0]["team"]["displayName"]

        # Default placeholders for pitchers (will fill if available)
        away_pitcher = "TBD"
        home_pitcher = "TBD"

        # Extract starting pitchers if available
        for comp in event["competitions"][0]["competitors"]:
            if "startingPitcher" in comp:
                pitcher_name = comp["startingPitcher"]["athlete"]["displayName"]
                if comp["homeAway"] == "home":
                    home_pitcher = pitcher_name
                else:
                    away_pitcher = pitcher_name

        games.append([game_time, away_team, home_team, away_pitcher, home_pitcher])
    return pd.DataFrame(games, columns=["Game Time", "Away Team", "Home Team", "Away Pitcher", "Home Pitcher"])


# -------------------------
# 2. Scrape Team NRFI Stats
# -------------------------
def fetch_team_nrfi_stats():
    url = "https://www.teamrankings.com/mlb/stat/1st-inning-runs-per-game"
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")

    table = soup.find("table", {"class": "tr-table"})
    rows = table.find_all("tr")[1:]

    stats = {}
    for row in rows:
        cols = [c.text.strip() for c in row.find_all("td")]
        if len(cols) >= 2:
            team = cols[0]
            first_inning_runs = float(cols[1])
            stats[team] = first_inning_runs
    return stats


# -------------------------
# 3. NRFI Model Formula
# -------------------------
def generate_nrfi_model():
    schedule = fetch_mlb_schedule()
    team_stats = fetch_team_nrfi_stats()

    results = []
    for _, row in schedule.iterrows():
        away_team = row["Away Team"]
        home_team = row["Home Team"]

        away_rpg = team_stats.get(away_team, 0.5)
        home_rpg = team_stats.get(home_team, 0.5)

        # Convert 1st inning runs per game to NRFI probability
        away_nrfi = max(0.2, 1 - away_rpg / 1.0)
        home_nrfi = max(0.2, 1 - home_rpg / 1.0)

        nrfi_prob = round((away_nrfi * home_nrfi) * 100, 1)
        pick = "NRFI" if nrfi_prob >= 55 else "YRFI"

        results.append([
            row["Game Time"], away_team, home_team, pick, nrfi_prob
        ])

    df = pd.DataFrame(results, columns=["Game Time", "Away Team", "Home Team", "Pick", "Confidence"])
    df.to_csv("nrfi_model.csv", index=False)
    print("✅ NRFI model updated with real data!")


# -------------------------
# 4. Run Daily
# -------------------------
if __name__ == "__main__":
    generate_nrfi_model()
