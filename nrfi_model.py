import pandas as pd
from datetime import datetime
from nrfi_model import generate_nrfi_model  # function that returns a dataframe
from daily_model import generate_daily_model  # function that returns a dataframe

def update_models():
    # === 1. Generate NRFI / YRFI Model ===
    try:
        nrfi_df = generate_nrfi_model()
        nrfi_filename = "nrfi_model.csv"
        nrfi_df.to_csv(nrfi_filename, index=False)
        print(f"[{datetime.now()}] NRFI model saved as {nrfi_filename}")
    except Exception as e:
        print(f"Error generating NRFI model: {e}")

if __name__ == "__main__":
    update_models()
