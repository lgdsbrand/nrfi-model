import pandas as pd
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -----------------------------
# GOOGLE SHEETS CONFIG
# -----------------------------
SHEET_NAME = "updateMLBDAILYMODEL"
TAB_NAME = "NRFI"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)

# -----------------------------
# SCRAPING FUNCTIONS
# -----------------------------

def get_mlb_schedule():
    """Pull today's MLB schedule from ESPN API"""
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
            "Game": f"{away['team']['abbreviation']} @ {home['team']['abbreviation']}",
            "Pitchers": f"{away.get('probablePitcher', {}).get('displayName','TBD')} vs {home.get('probablePitcher', {}).get('displayName','TBD')}",
            "Team NR": "TBD",
            "Pitcher NRFI": "TBD",
            "Model %": "TBD",
            "Pick": "TBD",
        })
    return pd.DataFrame(games)

def get_crowdsline_data():
    """
    Pull NRFI/YRFI data from TheCrowdsLine.ai API.
    This assumes theCrowdsLine.ai provides JSON with team & pitcher NRFI/YRFI % and 1st inning ERA.
    """
    url = "https://thecrowdsline.ai/mlb/nrfi-data"  # Example endpoint
    resp = requests.get(url).json()
    return pd.DataFrame(resp)

# -----------------------------
# NRFI CALCULATION LOGIC
# -----------------------------

def calculate_nrfi(df_schedule, df_crowds):
    """
    Merge schedule with NRFI data and calculate model % and pick
    """
    df = df_schedule.copy()

    # Merge logic example (requires matching by team abbreviations)
    # Assumes df_crowds has columns: AwayTeam, HomeTeam, AwayNRFI%, HomeNRFI%, AwayPitcherNRFI%, HomePitcherNRFI%
    df = df.merge(df_crowds, how="left", left_on="Game", right_on="Matchup")

    # Calculate model probability for NRFI
    # Simple formula: Combine team + pitcher NRFI averages
    df["Model %"] = (
        df["AwayNRFI%"] * df["AwayPitcherNRFI%"] +
        df["HomeNRFI%"] * df["HomePitcherNRFI%"]
    ) / 2

    df["Pick"] = df["Model %"].apply(lambda x: "NRFI" if x >= 0.55 else "YRFI")
    return df[["Game", "Pitchers", "Team NR", "Pitcher NRFI", "Model %", "Pick"]]

# -----------------------------
# MAIN UPDATE FUNCTION
# -----------------------------

def run_nrfi_model():
    schedule = get_mlb_schedule()
    crowds_data = get_crowdsline_data()
    df = calculate_nrfi(schedule, crowds_data)

    # Push to Google Sheet
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    return df

if __name__ == "__main__":
    df = run_nrfi_model()
    print("NRFI model updated to Google Sheet.")
