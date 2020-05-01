import os
from functools import wraps
from flask import request
import logging
import requests
import copy

from constants import REPLY_BLOCK, REPLY_TEXT, DIVIDER

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


def parse_player(players_text):

    players_list = players_text.split(",")
    players_list = [player.strip().title() for player in players_list]
    players_list = list(filter(None, players_list))

    return players_list


def post_slack_data(response_url, text, players, response_type="ephemereal"):

    text_to_show = copy.deepcopy(REPLY_TEXT)
    text_to_show["text"]["text"] = f"*{text}* \n {players}"

    main_block = copy.deepcopy(REPLY_BLOCK)

    main_block["blocks"].append(text_to_show)
    main_block["blocks"].append(DIVIDER)
    main_block["response_type"] = response_type

    resp = requests.post(
        response_url,
        json=main_block,
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": SLACK_TOKEN,
        },
    )

    logger.debug(f"Data posted to Slack: {main_block}")
    logger.debug(f"Status Code: {resp.status_code}, Text: {resp.text}")


def format_user(data):
    user_data = f"User: [{data['user_id']},{data['user_name']}]"

    return user_data


if __name__ == "__main__":
    pass
