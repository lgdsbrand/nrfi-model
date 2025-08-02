import pandas as pd
from datetime import datetime

def update_nrfi_model():
    # Dummy NRFI/YRFI data for testing
    games = [
        ["08:05 PM ET", "Detroit Tigers", "Philadelphia Phillies", "NRFI", 72],
        ["08:10 PM ET", "Houston Astros", "Boston Red Sox", "YRFI", 65],
    ]
    columns = ["Game Time", "Away Team", "Home Team", "Pick", "Confidence"]
    df = pd.DataFrame(games, columns=columns)

    df.to_csv("nrfi_model.csv", index=False)
    print(f"[{datetime.now()}] ✅ NRFI model updated")

if __name__ == "__main__":
    update_nrfi_model()
