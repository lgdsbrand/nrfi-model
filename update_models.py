import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

CSV_FILENAME = "nrfi_model.csv"

# --- 1. ESPN MLB Schedule ---
def get_espn_games():
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
    resp = requests.get(url).json()
    games = []
    for event in resp.get("events", []):
        game_time = datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ").strftime("%I:%M %p")
        teams = event["competitions"][0]["competitors"]
        home = next(t for t in teams if t["homeAway"] == "home")["team"]["displayName"]
        away = next(t for t in teams if t["homeAway"] == "away")["team"]["displayName"]
        games.append({"game_time": game_time, "home_team": home, "away_team": away})
    return pd.DataFrame(games)

# --- 2. Scrape TheCrowdsLine.ai for NRFI Data ---
def get_crowdsline_stats():
    url = "https://www.thecrowdsline.ai/mlb/nrfi"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # Example scrape: This needs adjustment based on live HTML
    data_rows = []
    rows = soup.select("table tr")
    for row in rows[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 8:
            data_rows.append({
                "away_team": cols[0],
                "home_team": cols[1],
                "away_pitcher_nrfi": float(cols[2].strip('%'))/100,
                "home_pitcher_nrfi": float(cols[3].strip('%'))/100,
                "away_team_nrfi": float(cols[4].strip('%'))/100,
                "home_team_nrfi": float(cols[5].strip('%'))/100,
                "away_pitcher_1st_era": float(cols[6]),
                "home_pitcher_1st_era": float(cols[7]),
                "ballpark_nrfi": float(cols[8].strip('%'))/100 if len(cols) > 8 else 0.65
            })

    return pd.DataFrame(data_rows)

# --- 3. Confidence Formula ---
def calculate_nrfi_conf(row):
    avg_pitcher_nrfi = (row["home_pitcher_nrfi"] + row["away_pitcher_nrfi"]) / 2
    avg_team_nrfi = (row["home_team_nrfi"] + row["away_team_nrfi"]) / 2
    ballpark = row["ballpark_nrfi"]
    era_factor = 1 - ((row["home_pitcher_1st_era"] + row["away_pitcher_1st_era"]) / 2) / 9

    nrfi_conf = avg_pitcher_nrfi * avg_team_nrfi * ballpark * era_factor * 100
    pick = "NRFI" if nrfi_conf >= 50 else "YRFI"
    confidence = round(max(nrfi_conf, 100 - nrfi_conf))
    return pd.Series([pick, confidence])

# --- 4. Main Function ---
def main():
    games_df = get_espn_games()
    crowdsline_df = get_crowdsline_stats()

    # Merge on teams
    df = pd.merge(games_df, crowdsline_df, on=["home_team", "away_team"], how="left")

    # Compute pick & confidence
    df[["Pick", "Confidence"]] = df.apply(calculate_nrfi_conf, axis=1)

    # Save CSV for Streamlit
    output_df = df[["game_time", "away_team", "home_team", "Pick", "Confidence"]]
    output_df.to_csv(CSV_FILENAME, index=False)
    print(f"NRFI model updated: {CSV_FILENAME}")

if __name__ == "__main__":
    main()
