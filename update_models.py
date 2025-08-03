import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
CSV_FILE = "nrfi_model.csv"

# -----------------------------
# SCRAPING FUNCTIONS
# -----------------------------

def get_mlb_schedule():
    """
    Pull today's MLB schedule from ESPN API.
    Returns DataFrame with game time, teams, and pitchers.
    """
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()

    games = []
    for event in resp.get("events", []):
        comp = event["competitions"][0]
        home = comp["competitors"][0]
        away = comp["competitors"][1]

        game_time = datetime.fromisoformat(comp["date"][:-1]).strftime("%I:%M %p")

        games.append({
            "Time": game_time,
            "Away Team": away["team"]["displayName"],
            "Home Team": home["team"]["displayName"],
            "Away Pitcher": away.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD"),
            "Home Pitcher": home.get("probables", [{}])[0].get("athlete", {}).get("displayName", "TBD"),
        })

    return pd.DataFrame(games)


def get_crowdsline_data():
    """
    Scrapes NRFI/YRFI data from TheCrowdsLine.ai (sample mock).
    Replace with actual scraper if needed.
    """
    # Mock structure: You can implement BeautifulSoup if needed for full automation
    # These would be keyed by team name or pitcher name in production
    return {
        "team_nrfi%": 0.70,
        "opp_nrfi%": 0.72,
        "pitcher_nrfi%": 0.80,
        "opp_pitcher_nrfi%": 0.78,
        "ballpark_nrfi%": 0.65,
        "first_inning_rpg": 0.48,
        "first_inning_rpga": 0.52
    }


def calculate_nrfi_confidence(row):
    """
    Full NRFI/YRFI formula combining pitchers, teams, ballpark, and 1st inning stats.
    """

    # Simulated data from CrowdsLine for now
    stats = get_crowdsline_data()

    team_avg = (stats["team_nrfi%"] + stats["opp_nrfi%"]) / 2
    pitcher_avg = (stats["pitcher_nrfi%"] + stats["opp_pitcher_nrfi%"]) / 2
    ballpark = stats["ballpark_nrfi%"]
    inning_factor = 1 - ((stats["first_inning_rpg"] + stats["first_inning_rpga"]) / 2)

    # Weighted formula for NRFI probability
    nrfi_prob = (team_avg * 0.35) + (pitcher_avg * 0.35) + (ballpark * 0.15) + (inning_factor * 0.15)

    pick = "NRFI" if nrfi_prob >= 0.6 else "YRFI"
    return round(nrfi_prob * 100), pick


# -----------------------------
# MAIN LOGIC
# -----------------------------

def generate_nrfi_model():
    schedule_df = get_mlb_schedule()

    if schedule_df.empty:
        print("No MLB games found for today.")
        return

    schedule_df[["NRFI Confidence %", "Pick"]] = schedule_df.apply(
        lambda row: pd.Series(calculate_nrfi_confidence(row)),
        axis=1
    )

    # Sort: Highest confidence first
    schedule_df = schedule_df.sort_values("NRFI Confidence %", ascending=False)

    # Save to CSV
    schedule_df.to_csv(CSV_FILE, index=False)
    print(f"NRFI model updated: {CSV_FILE}")


if __name__ == "__main__":
    generate_nrfi_model()
