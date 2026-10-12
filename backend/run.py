import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    print("[*] Starting AI-Based NIDS Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
