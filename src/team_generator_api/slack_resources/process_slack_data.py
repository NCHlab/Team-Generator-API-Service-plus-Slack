
import copy
import threading
from threading import Lock
import requests
import json

from flask_restful import Resource, reqparse
from flask import Flask, Blueprint, request, Response

from config import login_required
import config


mutex = Lock()


class SlackData(Resource):
    def post(self):
        data = dict(request.form)
        data["payload"] = json.loads(data["payload"])

        thread = threading.Thread(target=self.process_tg_modal_data, args=(data,))
        thread.start()
        return Response(status=200)

    def process_tg_modal_data(self, data):

        if data["payload"]["type"] == "block_actions":
            config.slack_player_data.append(data)
            # print("ADDED TO PLAYER_DATA")
        elif data["payload"]["type"] == "view_submission":

            num_of_team = data["payload"]["view"]["state"]["values"]["num_of_teams"][
                "num_of_teams_action"
            ]["selected_option"]["value"]
            response_url = data["payload"]["response_urls"][0]["response_url"]

            # print(config.slack_player_data)
            # print(response_url)
            # print(num_of_team)
            # print(config.slack_player_data[-1]["payload"]["actions"][0]["selected_options"])

            users_selected = list(
                map(
                    lambda x: x["value"],
                    config.slack_player_data[-1]["payload"]["actions"][0][
                        "selected_options"
                    ],
                )
            )
            # print(users_selected)

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
    
    print(user_teams)

    for e, team in enumerate(user_teams):

        resp = requests.post(
            response_url,
            json={
                "response_type": "in_channel",
                "text": f"TEAM {e+1}\n" + "\n".join(team),
            },
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        print(resp.status_code)
        print(resp.text)