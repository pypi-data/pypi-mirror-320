import os
from fastapi import FastAPI
from .app.api import setup_routes
import uvicorn

# Create the FastAPI app
app = FastAPI()

# Set up routes
setup_routes(app)

def spin_up():
    """
    Spin up the FastAPI app using Uvicorn.
    """
    port = int(os.getenv("APP_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Optional: Allow running the app directly via `python main.py`
if __name__ == "__main__":
    spin_up()
