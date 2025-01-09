from app import app
from waitress import serve
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="127.0.0.1", port=port)
