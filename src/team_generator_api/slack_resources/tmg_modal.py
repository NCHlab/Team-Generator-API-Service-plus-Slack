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


class SlackInitialMsg(Resource):
    def post(self):
        data = dict(request.form)

        triggerid = data["trigger_id"]

        logger.info(f"Req from slack to trigger modal, ID: {triggerid}")

        # Start a different thread to process the post request for modal
        thread = threading.Thread(target=send_slack_modal, args=(triggerid,))
        thread.start()

        # Immediately send back empty HTTP 200 response
        return Response(status=200)


def create_slack_modal(triggerid):

    team_data = json_local_load()
    player_names = team_data["names"]

    PLAYER_MODAL_OBJ["trigger_id"] = triggerid

    option_list = []

    for e, name in enumerate(player_names):

        newdict = copy.deepcopy(PLAYER_CHECKBOX)
        newdict["text"]["text"] = name
        newdict["value"] = name
        option_list.append(newdict)

    PLAYER_MODAL_OBJ["view"]["blocks"][5]["accessory"]["options"] = option_list

    logger.debug(f"Object Created: {PLAYER_MODAL_OBJ}")

    return PLAYER_MODAL_OBJ


def send_slack_modal(triggerid):

    data = create_slack_modal(triggerid)

    logger.info("Sending Modal to Slack")

    res = requests.post(
        "https://slack.com/api/views.open",
        json=data,
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": config.SLACK_TOKEN,
        },
    )
    resp = res.json()
    logger.debug(f"Slack Response: {resp}")
