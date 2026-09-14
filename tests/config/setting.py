import os
ENV = os.getenv("TEST_ENV", "dev")
TEST_ENV = {
    "dev": {
        "BASE_URL": "http://localhost:5001",
        "API_PREFIX": "/api/notes"
    },}

config = TEST_ENV[ENV]
BASE_URL = config["BASE_URL"]
API_PREFIX = config["API_PREFIX"]
