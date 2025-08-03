import pandas as pd
import numpy as np

# Load CSVs
TEAM_FILE = "team_nrfi.csv"
PITCHER_FILE = "pitcher_nrfi.csv"

def get_today_games():
    """
    For now, this simulates the matchups using CSVs.
    Later you can replace with ESPN/FanDuel scraping.
    """
    # Example: Combine first N pitchers and teams into matchups
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    # Simulate games based on CSV order
    games = []
    for i in range(min(len(teams), len(pitchers)//2)):
        home_team = teams.iloc[i % len(teams)]["Team"]
        away_team = teams.iloc[(i+1) % len(teams)]["Team"]

        home_pitcher = pitchers.iloc[i*2 % len(pitchers)]["Pitcher"]
        away_pitcher = pitchers.iloc[(i*2+1) % len(pitchers)]["Pitcher"]

        games.append({
            "Game Time": f"{3+i}:00 PM",
            "Matchup": f"{away_team} @ {home_team}",
            "Home Team": home_team,
            "Away Team": away_team,
            "Pitchers": f"{away_pitcher} vs {home_pitcher}"
        })

    return pd.DataFrame(games)


def calculate_nrfi(games_df):
    """Calculate NRFI%, YRFI%, and confidence from CSV stats."""
    teams = pd.read_csv(TEAM_FILE)
    pitchers = pd.read_csv(PITCHER_FILE)

    results = []
    for _, game in games_df.iterrows():
        home_team = game["Home Team"]
        away_team = game["Away Team"]

        # Get team stats
        home_stats = teams[teams["Team"] == home_team].iloc[0]
        away_stats = teams[teams["Team"] == away_team].iloc[0]

        # Get pitcher stats
        home_pitcher = game["Pitchers"].split(" vs ")[1]
        away_pitcher = game["Pitchers"].split(" vs ")[0]

        home_pitcher_stats = pitchers[pitchers["Pitcher"] == home_pitcher].iloc[0]
        away_pitcher_stats = pitchers[pitchers["Pitcher"] == away_pitcher].iloc[0]

        # Weighted NRFI formula (simple avg for now)
        nrfi_score = np.mean([
            home_stats["NRFI%"],
            away_stats["NRFI%"],
            home_pitcher_stats["NRFI%"],
            away_pitcher_stats["NRFI%"]
        ])

        # Confidence = distance from 50
        confidence = abs(nrfi_score - 50)

        # Determine NRFI or YRFI
        prediction = "NRFI" if nrfi_score >= 50 else "YRFI"

        results.append({
            "Game Time": game["Game Time"],
            "Matchup": game["Matchup"],
            "Pitchers": game["Pitchers"],
            "Prediction": prediction,
            "NRFI %": round(nrfi_score, 1),
            "Confidence": round(confidence, 1)
        })

    df = pd.DataFrame(results)
    return df


def main():
    """Generate today's NRFI model and save to CSV."""
    games = get_today_games()
    df = calculate_nrfi(games)
    df.to_csv("nrfi_model.csv", index=False)
    print(df)
    return df


if __name__ == "__main__":
    main()
