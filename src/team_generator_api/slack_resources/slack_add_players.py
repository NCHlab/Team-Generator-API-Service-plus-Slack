import threading
from threading import Lock
import requests
import logging
import copy

from flask_restful import Resource, reqparse
from flask import Flask, request, Response

from constants import REPLY_BLOCK, REPLY_TEXT, DIVIDER
import config


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

    players_list = players_text.split(",")
    players_list = [x.strip().title() for x in players_list]
    players_list = list(filter(None, players_list))

    mutex.acquire()

    returned_data = []
    for player in players_list:
        resp = config.obj.add_mode(player)
        returned_data.append(resp)

    mutex.release()

    players_ok = list(filter(lambda x: x["status"] == "ok", returned_data))

    if len(returned_data) == len(players_ok):
        players_ok = list(map(lambda x: x["name"], players_ok))

        post_slack_data(response_url, f"Players Added:", ", ".join(players_ok))
    else:
        players_error = list(filter(lambda x: x["status"] == "error", returned_data))
        players_error = list(map(lambda x: x["name"], players_error))

        post_slack_data(
            response_url, "Following players already exist", ", ".join(players_error)
        )


def post_slack_data(response_url, text, players):

    text_to_show = copy.deepcopy(REPLY_TEXT)
    text_to_show["text"]["text"] = f"*{text}* \n {players}"

    main_block = copy.deepcopy(REPLY_BLOCK)

    main_block["blocks"].append(text_to_show)
    main_block["blocks"].append(DIVIDER)
    main_block["response_type"] = "ephemereal"

    resp = requests.post(
        response_url,
        json=main_block,
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": config.SLACK_TOKEN,
        },
    )

    logger.debug(f"Data posted to Slack: {main_block}")
    logger.debug(f"Status Code: {resp.status_code}, Text: {resp.text}")
