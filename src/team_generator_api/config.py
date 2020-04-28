import os
from functools import wraps
from flask import request
import logging

logger = logging.getLogger(__name__)

# Require Token to use the API Web Service
ACCESS_TOKEN = os.environ["TMG_API_TOKEN"]

try:
    SLACK_TOKEN = os.environ["SLACK_TOKEN"]
except KeyError:
    print("SLACK_TOKEN ENVIRONMENT VARIABLE NOT SET")

slack_player_data = []
obj = None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        Auth = request.headers.get("Authorization", "")
        if not Auth:
            return {"message": "Authorization Required in Header"}, 401

        elif Auth[7:] != ACCESS_TOKEN:
            return {"message": "UnAuthorized Access! Credentials Incorrect"}, 401

        return f(*args, **kwargs)

    return decorated_function


if __name__ == "__main__":
    pass
