import os

import requests

from pipeline_ui.modules.common.dependencies import INTERNAL_SERVER_URL


def write_access_token(access_token: str):
    cache_dir = os.path.expanduser("~/.cache/pipeline-ui")
    os.makedirs(cache_dir, exist_ok=True)
    token_file = os.path.join(cache_dir, "token")

    with open(token_file, "w") as f:
        f.write(access_token + "\n")

    print(f"Access token saved to {token_file}")


def load_access_token() -> str:
    cache_dir = os.path.expanduser("~/.cache/pipeline-ui")
    os.makedirs(cache_dir, exist_ok=True)
    token_file = os.path.join(cache_dir, "token")

    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            return f.read().decode("utf-8").strip()

    raise Exception("No access token found. Please login first.")


def check_access_token(access_token: str):


    response = requests.get(
        f"{INTERNAL_SERVER_URL}/auth/check-api-token-access",
        headers={"X-API-Key": access_token}
    )
    if response.status_code == 200:
        return True
    else:
        return False