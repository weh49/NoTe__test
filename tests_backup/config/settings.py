import os

ENV = os.getenv("TEST_ENV", "dev")

ENVIRONMENTS = {
    "dev": {
        "BASE_URL": "http://localhost:5001",
        "API_PREFIX": "/api/notes"
    },
    "staging": {
        "BASE_URL": "https://staging-api.example.com",
        "API_PREFIX": "/api/notes"
    }
}

config = ENVIRONMENTS[ENV]
BASE_URL = config["BASE_URL"]
API_PREFIX = config["API_PREFIX"]
