import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# -----------------------------
# 1. Fetch today's MLB games
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

        home_pitcher = home.get("probables", [{}])[0].get("displayName", "TBD")
        away_pitcher = away.get("probables", [{}])[0].get("displayName", "TBD")

        games.append({
            "Game Time": game_time,
            "Matchup": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Home Team": home['team']['displayName'],
            "Away Team": away['team']['displayName'],
            "Home Pitcher": home_pitcher,
            "Away Pitcher": away_pitcher
        })

    return pd.DataFrame(games)


# -----------------------------
# 2. Scrape TheCrowdsLine.ai NRFI stats
# -----------------------------
def scrape_crowdsline_stats():
    url = "https://thecrowdsline.ai/mlb/nrfi"  # Example NRFI/YRFI stats page
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # This assumes table rows <tr> for team/pitcher NRFI stats exist on the page
    # You may need to adjust selectors depending on the exact HTML
    team_stats = {}
    pitcher_stats = {}

    for row in soup.find_all("tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) >= 4:
            name = cells[0]
            nrfi_pct = float(cells[1].replace("%","")) if "%" in cells[1] else None
            era_1st = float(cells[2]) if cells[2].replace(".","",1).isdigit() else None

            if "Team" in row.get("class", []):  # Hypothetical class for team rows
                team_stats[name] = {"NRFI%": nrfi_pct, "YRFI%": 100 - nrfi_pct}
            else:
                pitcher_stats[name] = {"NRFI%": nrfi_pct, "ERA_1st": era_1st}

    return team_stats, pitcher_stats


# -----------------------------
# 3. Calculate NRFI/YRFI Prediction
# -----------------------------
def calculate_nrfi(df, team_stats, pitcher_stats):
    results = []

    for _, row in df.iterrows():
        home_pitcher = row["Home Pitcher"]
        away_pitcher = row["Away Pitcher"]

        # Skip prediction if TBD pitcher
        if "TBD" in home_pitcher or "TBD" in away_pitcher:
            results.append({**row, "Pitchers": f"{away_pitcher} vs {home_pitcher}", 
                            "Prediction": "", "Confidence %": ""})
            continue

        home_team = row["Home Team"]
        away_team = row["Away Team"]

        # Get stats or defaults
        home_team_nrfi = team_stats.get(home_team, {"NRFI%": 60})["NRFI%"]
        away_team_nrfi = team_stats.get(away_team, {"NRFI%": 60})["NRFI%"]

        home_pitcher_nrfi = pitcher_stats.get(home_pitcher, {"NRFI%": 60})["NRFI%"]
        away_pitcher_nrfi = pitcher_stats.get(away_pitcher, {"NRFI%": 60})["NRFI%"]

        home_pitcher_era = pitcher_stats.get(home_pitcher, {"ERA_1st": 2.0})["ERA_1st"]
        away_pitcher_era = pitcher_stats.get(away_pitcher, {"ERA_1st": 2.0})["ERA_1st"]

        avg_era = (home_pitcher_era + away_pitcher_era) / 2.0

        # Weighted formula
        confidence = round(
            ((home_team_nrfi + away_team_nrfi) * 0.4 +
             (home_pitcher_nrfi + away_pitcher_nrfi) * 0.4 +
             (100 - avg_era*20) * 0.2) / 2,
            1
        )

        prediction = "NRFI" if confidence >= 60 else "YRFI"

        results.append({
            **row,
            "Pitchers": f"{away_pitcher} vs {home_pitcher}",
            "Prediction": prediction,
            "Confidence %": confidence
        })

    return pd.DataFrame(results)[
        ["Game Time", "Matchup", "Pitchers", "Prediction", "Confidence %"]
    ]


# -----------------------------
# 4. Main Script
# -----------------------------
if __name__ == "__main__":
    games_df = get_today_games()
    team_stats, pitcher_stats = scrape_crowdsline_stats()
    final_df = calculate_nrfi(games_df, team_stats, pitcher_stats)

    final_df.to_csv("nrfi_model.csv", index=False)
    print("NRFI model updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
