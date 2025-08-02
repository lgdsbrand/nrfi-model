from datetime import datetime
from nrfi_model import generate_nrfi_model

def update_models():
    try:
        generate_nrfi_model()
        print(f"[{datetime.now()}] ✅ NRFI model CSV generated")
    except Exception as e:
        print(f"❌ Error generating NRFI model: {e}")

if __name__ == "__main__":
    update_models()
