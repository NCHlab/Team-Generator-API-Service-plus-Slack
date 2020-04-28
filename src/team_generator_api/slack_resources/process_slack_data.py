
import copy
import threading
from threading import Lock
import requests
import json
import logging

from flask_restful import Resource, reqparse
from flask import Flask, Blueprint, request, Response

from config import login_required
import config

logger = logging.getLogger(__name__)
mutex = Lock()


class SlackData(Resource):
    def post(self):
        data = dict(request.form)
        data["payload"] = json.loads(data["payload"])

        logger.debug(f"Post Req Received from Slack: {data['payload']}")

        thread = threading.Thread(target=self.process_tg_modal_data, args=(data,))
        thread.start()
        return Response(status=200)

    def process_tg_modal_data(self, data):

        if data["payload"]["type"] == "block_actions":
            config.slack_player_data.append(data)
            logger.debug(f"data appended to slack_player_data")

        elif data["payload"]["type"] == "view_submission":

            num_of_team = data["payload"]["view"]["state"]["values"]["num_of_teams"][
                "num_of_teams_action"
            ]["selected_option"]["value"]
            response_url = data["payload"]["response_urls"][0]["response_url"]


            logger.debug(f"Response URL: {response_url}, Num Of Team: {num_of_team}")
            logger.debug(f"Selected Options: {config.slack_player_data[-1]['payload']['actions'][0]['selected_options']}")

            users_selected = list(
                map(
                    lambda x: x["value"],
                    config.slack_player_data[-1]["payload"]["actions"][0][
                        "selected_options"
                    ],
                )
            )
            logger.debug(f"users_selected: {users_selected}")

            # Emptying Global Object
            config.slack_player_data = []

            activate_players_post_to_slack(users_selected, num_of_team, response_url)


def activate_players_post_to_slack(users_selected, num_of_team, response_url):

    mutex.acquire()

    config.obj.set_all_players(activate=False)
    config.obj.update_mode(int(num_of_team))

    for player in users_selected:
        config.obj.activate_player(player)

    user_teams = config.obj.get_teams()

    mutex.release()
    
    logger.debug(f"Team Data: {user_teams}")

    for e, team in enumerate(user_teams):

        resp = requests.post(
            response_url,
            json={
                "response_type": "in_channel",
                "text": f"TEAM {e+1}\n" + "\n".join(team),
            },
            headers={"Content-Type": "application/json;charset=utf-8"},
        )
        logger.debug(f"Status Code: {resp.status_code}, Text: {resp.text}")