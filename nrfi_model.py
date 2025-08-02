import pandas as pd
import requests
from datetime import datetime

# --- CONFIG ---
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

def fetch_espn_games():
    """Fetch today's MLB games from ESPN API."""
    today = datetime.now().strftime("%Y%m%d")
    url = f"{ESPN_URL}?dates={today}"
    data = requests.get(url).json()

    games = []
    for event in data.get("events", []):
        game_time = datetime.fromisoformat(event["date"].replace("Z", "+00:00")).strftime("%I:%M %p ET")
        competitors = event["competitions"][0]["competitors"]
        home = next(team for team in competitors if team["homeAway"] == "home")["team"]["displayName"]
        away = next(team for team in competitors if team["homeAway"] == "away")["team"]["displayName"]
        games.append([game_time, away, home])
    return pd.DataFrame(games, columns=["Game Time", "Away Team", "Home Team"])


def generate_nrfi_confidence(row):
    """
    Example formula combining team, pitcher, and park factors.
    Replace dummy stats with your scraped real stats later.
    """
    # Dummy lookup (replace with real team/pitcher stats dict)
    team_nrfi = 0.70
    opp_nrfi = 0.68
    pitcher_nrfi = 0.82
    park_factor = 0.50  # 0.5 neutral, <0.5 favors NRFI, >0.5 favors YRFI

    # Weighted confidence formula (adjust as needed)
    nrfi_conf = (
        (team_nrfi + opp_nrfi) / 2 * 0.4 +
        pitcher_nrfi * 0.4 +
        (1 - park_factor) * 0.2
    )

    # Convert to %
    nrfi_conf = round(nrfi_conf * 100)

    # Determine Pick
    if nrfi_conf >= 60:  # confident in NRFI
        return "NRFI", nrfi_conf
    else:  # otherwise YRFI
        return "YRFI", 100 - nrfi_conf


def generate_nrfi_model():
    games_df = fetch_espn_games()
    picks = []
    for _, row in games_df.iterrows():
        pick, conf = generate_nrfi_confidence(row)
        picks.append([row["Game Time"], row["Away Team"], row["Home Team"], pick, conf])
    return pd.DataFrame(picks, columns=["Game Time", "Away Team", "Home Team", "Pick", "Confidence"])


if __name__ == "__main__":
    df = generate_nrfi_model()
    df.to_csv("nrfi_model.csv", index=False)
    print(f"✅ NRFI model generated with {len(df)} games.")
