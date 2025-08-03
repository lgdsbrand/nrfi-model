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


def get_crowdsline_stats(home_team, away_team):
    """
    Stub function to simulate per-game NRFI stats.
    Replace this with a proper scrape/API pull from TheCrowdsLine.ai or other source.
    """
    import random

    # Simulate variation
    return {
        "home_team_nrfi%": random.uniform(0.55, 0.85),
        "away_team_nrfi%": random.uniform(0.55, 0.85),
        "home_pitcher_nrfi%": random.uniform(0.6, 0.9),
        "away_pitcher_nrfi%": random.uniform(0.6, 0.9),
        "ballpark_nrfi%": random.uniform(0.5, 0.75),
        "home_pitcher_era_1st": random.uniform(0.0, 1.5),
        "away_pitcher_era_1st": random.uniform(0.0, 1.5),
        "first_inning_rpg_home": random.uniform(0.4, 0.7),
        "first_inning_rpg_away": random.uniform(0.4, 0.7),
    }


def calculate_nrfi_confidence(row):
    """
    Full NRFI/YRFI formula combining pitchers, teams, ballpark, and 1st inning stats.
    Returns (confidence %, pick)
    """
    stats = get_crowdsline_stats(row["Home Team"], row["Away Team"])

    # Calculate averages
    team_avg = (stats["home_team_nrfi%"] + stats["away_team_nrfi%"]) / 2
    pitcher_avg = (stats["home_pitcher_nrfi%"] + stats["away_pitcher_nrfi%"]) / 2
    ballpark = stats["ballpark_nrfi%"]

    # Factor in 1st inning ERA as a negative factor for NRFI
    era_factor = 1 - ((stats["home_pitcher_era_1st"] + stats["away_pitcher_era_1st"]) / 6)  # normalize ~0-1
    inning_factor = 1 - ((stats["first_inning_rpg_home"] + stats["first_inning_rpg_away"]) / 2)

    # Weighted formula for NRFI probability
    nrfi_prob = (
        team_avg * 0.30 +
        pitcher_avg * 0.35 +
        ballpark * 0.10 +
        era_factor * 0.15 +
        inning_factor * 0.10
    )

    # Clamp between 0 and 1
    nrfi_prob = max(0, min(nrfi_prob, 1))

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

    # Compute NRFI/YRFI predictions
    schedule_df[["Confidence %", "Pick"]] = schedule_df.apply(
        lambda row: pd.Series(calculate_nrfi_confidence(row)),
        axis=1
    )

    # Sort highest confidence first
    schedule_df = schedule_df.sort_values("Confidence %", ascending=False)

    # Save to CSV for Streamlit app
    schedule_df.to_csv(CSV_FILE, index=False)
    print(f"NRFI model updated: {CSV_FILE}")


if __name__ == "__main__":
    generate_nrfi_model()
