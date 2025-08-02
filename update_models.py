from nrfi_model import generate_nrfi_model
from datetime import datetime

def update_nrfi_model():
    df = generate_nrfi_model()
    df.to_csv("nrfi_model.csv", index=False)
    print(f"[{datetime.now()}] ✅ NRFI model updated: {len(df)} games")

if __name__ == "__main__":
    update_nrfi_model()
