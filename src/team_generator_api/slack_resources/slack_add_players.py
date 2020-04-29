import copy
import threading
from threading import Lock
import requests
import logging

from flask_restful import Resource, reqparse
from flask import Flask, Blueprint, request, Response

from config import login_required
import config

from generic_gen_teams import json_local_load
from constants import PLAYER_MODAL_OBJ, PLAYER_CHECKBOX

logger = logging.getLogger(__name__)
mutex = Lock()


class SlackAddPlayer(Resource):
    def post(self):
        data = dict(request.form)

        response_url = data["response_url"]
        players_text = data["text"]

        logger.info(f"Req from slack to add players, Names: {players_text}")

        # # Start a different thread to process the post request for response
        thread = threading.Thread(
            target=process_players, args=(response_url, players_text)
        )
        thread.start()

        # Immediately send back empty HTTP 200 response
        return Response(status=200)


def process_players(response_url, players_text):

    player_list = players_text.split(",")
    players_list = [x.strip().title() for x in player_list]

    mutex.acquire()

    returned_data = []
    for player in players_list:
        resp = config.obj.add_mode(player)
        returned_data.append(resp)

    mutex.release()

    players_ok = list(filter(lambda x: x["status"] == "ok", returned_data))

    if len(returned_data) == len(players_ok):
        players_ok = list(map(lambda x: x["name"], players_ok))
        response = ({"text": f"Users Added: {', '.join(players_ok)}"}, 201)

        post_slack_data(
            response_url, {"text": f"Players Added: {', '.join(players_ok)}"}
        )
    else:
        players_error = list(filter(lambda x: x["status"] == "error", returned_data))
        players_error = list(map(lambda x: x["name"], players_error))

        post_slack_data(
            response_url, {"text": f"Players already exist: {', '.join(players_error)}"}
        )


def post_slack_data(response_url, data):

    resp = requests.post(
        response_url,
        json=data,
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": config.SLACK_TOKEN,
        },
    )

    logger.debug(f"Data posted to Slack: {data}")
    logger.debug(f"Status Code: {resp.status_code}, Text: {resp.text}")
