import pandas as pd
import requests
from datetime import datetime
import pytz

# --------- NRFI / YRFI MODEL ---------
def generate_nrfi_model():
    today = datetime.now().strftime("%Y%m%d")
    espn_url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    data = requests.get(espn_url).json()

    games = []
    eastern = pytz.timezone("US/Eastern")

    for event in data.get("events", []):
        game_time_utc = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        game_time_est = game_time_utc.astimezone(eastern).strftime("%I:%M %p ET")

        away_team = event["competitions"][0]["competitors"][1]["team"]["displayName"]
        home_team = event["competitions"][0]["competitors"][0]["team"]["displayName"]

        # Example confidence formula (replace with your real stats later)
        # Dummy logic: team name lengths as confidence proxy
        nrfi_conf = min(95, max(50, len(away_team) * 3))  
        yrfi_conf = 100 - nrfi_conf

        if nrfi_conf >= yrfi_conf:
            pick = "NRFI"
            conf = nrfi_conf
        else:
            pick = "YRFI"
            conf = yrfi_conf

        games.append([game_time_est, away_team, home_team, pick, conf])

    df = pd.DataFrame(games, columns=["Game Time", "Away Team", "Home Team", "Pick", "Confidence %"])
    df.sort_values(by="Confidence %", ascending=False, inplace=True)
    df.to_csv("nrfi_model.csv", index=False)
    print(f"[{datetime.now()}] ✅ NRFI model updated with {len(df)} games")
    return df

if __name__ == "__main__":
    generate_nrfi_model()
