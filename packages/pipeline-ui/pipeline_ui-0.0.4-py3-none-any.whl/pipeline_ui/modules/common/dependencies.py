import os
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development") #TODO to change to production when launch
if ENVIRONMENT == "development":
    INTERNAL_SERVER_URL = "http://localhost:8014"
elif ENVIRONMENT == "production":
    INTERNAL_SERVER_URL = "https://api.pipeline-ui.com"
else:
    raise ValueError(f"Invalid environment: {ENVIRONMENT}")
