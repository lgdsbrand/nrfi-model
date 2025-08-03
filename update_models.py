import pandas as pd
from datetime import datetime
from nrfi_model import generate_nrfi_model

def update_models():
    try:
        nrfi_df = generate_nrfi_model()
        filename = "nrfi_model.csv"
        nrfi_df.to_csv(filename, index=False)
        print(f"[{datetime.now()}] ✅ NRFI Model updated and saved to {filename}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error updating NRFI model: {e}")

if __name__ == "__main__":
    update_models()
