import copy
import logging
import random
import requests
import threading
import json

from flask_restful import Resource, reqparse
from flask import Flask, Blueprint, request, Response

from constants import REPLY_BLOCK, REPLY_TEXT, DIVIDER
import config

logger = logging.getLogger(__name__)
mutex = threading.Lock()


class SlackData(Resource):
    def post(self):
        data = dict(request.form)
        data["payload"] = json.loads(data["payload"])

        logger.debug(f"Post Req Received from Slack: {data['payload']}")

        thread = threading.Thread(target=process_tg_modal_data, args=(data,))
        thread.start()
        return Response(status=200)


def process_tg_modal_data(data):

    if data["payload"]["type"] == "block_actions":
        add_data_to_state(data)

    elif data["payload"]["type"] == "view_submission":

        users_selected, num_of_team, response_url = process_submission(data)
        reset_state_data()

        user_teams = activate_players(users_selected, num_of_team)
        main_block_message = create_message(user_teams)
        post_to_slack(main_block_message, response_url)


def add_data_to_state(data):
    config.slack_player_data.append(data)
    logger.debug(f"data appended to slack_player_data")


def reset_state_data():
    # Emptying Global Object
    config.slack_player_data = []


def process_submission(data):

    num_of_team = data["payload"]["view"]["state"]["values"]["num_of_teams"][
        "num_of_teams_action"
    ]["selected_option"]["value"]

    response_url = data["payload"]["response_urls"][0]["response_url"]

    logger.debug(f"Response URL: {response_url}, Num Of Team: {num_of_team}")
    logger.debug(
        f"Selected Options: {config.slack_player_data[-1]['payload']['actions'][0]['selected_options']}"
    )

    users_selected = list(
        map(
            lambda x: x["value"],
            config.slack_player_data[-1]["payload"]["actions"][0]["selected_options"],
        )
    )
    logger.debug(f"users_selected: {users_selected}")

    return (users_selected, num_of_team, response_url)


def activate_players(users_selected, num_of_team):

    mutex.acquire()

    config.obj.set_all_players(activate=False)
    config.obj.update_mode(int(num_of_team))

    for player in users_selected:
        config.obj.activate_player(player)

    user_teams = config.obj.get_teams()

    mutex.release()

    return user_teams


def create_message(user_teams):
    logger.debug(f"Team Data: {user_teams}")

    emojis = [
        ":smile:",
        ":joy:",
        ":cry:",
        ":unamused:",
        ":rolling_on_the_floor_laughing:",
        ":boom:",
        ":skull:",
        ":sob:",
        ":exploding_head:",
    ]

    text_block = []

    for e, team in enumerate(user_teams):
        newdict = copy.deepcopy(REPLY_TEXT)
        newdict["text"]["text"] = f"*TEAM {e+1}* {random.choice(emojis)}\n" + "\n".join(
            team
        )
        text_block.append(newdict)
        text_block.append(DIVIDER)

    main_block = copy.deepcopy(REPLY_BLOCK)

    main_block["blocks"] = text_block
    main_block["response_type"] = "in_channel"

    return main_block


def post_to_slack(main_block_message, response_url):

    resp = requests.post(
        response_url,
        json=main_block_message,
        headers={"Content-Type": "application/json;charset=utf-8"},
    )
    logger.debug(f"Status Code: {resp.status_code}, Text: {resp.text}")
