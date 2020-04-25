import os
from functools import wraps
import json
import copy

from flask_restful import Api, Resource, reqparse
from flask import Flask, Blueprint, request, Response
from generic_gen_teams import App, json_local_load, split_list

import requests
import threading
from constants import PLAYER_MODAL_OBJ, PLAYER_CHECKBOX

# from flask_restful import Api
# from myapi.resources.add_players import AddPlayers
# from myapi.resources.bar import Bar
# from myapi.resources.baz import Baz

app = Flask(__name__)
# api = Api(app)

blueprint = Blueprint("api", __name__, url_prefix="/v1")
api = Api(blueprint)
app.register_blueprint(blueprint)

obj = App()

# Require Token to use the API
ACCESS_TOKEN = os.environ["TMG_API_TOKEN"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]

list_of_teams = []
slack_player_data = []


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

    # print(PLAYER_MODAL_OBJ)

    return PLAYER_MODAL_OBJ


def send_slack_modal(triggerid):

    data = create_slack_modal(triggerid)

    res = requests.post(
        "https://slack.com/api/views.open",
        json=data,
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": SLACK_TOKEN,
        },
    )

    # resp = res.json()
    # print(resp)


def activate_players_post_to_slack(users_selected, num_of_team, response_url):

    obj.set_all_players(activate=False)
    obj.update_mode(int(num_of_team))

    for player in users_selected:
        obj.activate_player(player)

    user_teams = obj.get_teams()
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


class SlackData(Resource):
    def post(self):
        data = dict(request.form)
        data["payload"] = json.loads(data["payload"])

        thread = threading.Thread(target=self.process_tg_modal_data, args=(data,))
        thread.start()
        return Response(status=200)

    def process_tg_modal_data(self, data):
        global slack_player_data

        if data["payload"]["type"] == "block_actions":
            slack_player_data.append(data)
            # print("ADDED TO PLAYER_DATA")
        elif data["payload"]["type"] == "view_submission":

            num_of_team = data["payload"]["view"]["state"]["values"]["num_of_teams"][
                "num_of_teams_action"
            ]["selected_option"]["value"]
            response_url = data["payload"]["response_urls"][0]["response_url"]

            # print(slack_player_data)
            # print(response_url)
            # print(num_of_team)
            # print(slack_player_data[-1]["payload"]["actions"][0]["selected_options"])

            users_selected = list(
                map(
                    lambda x: x["value"],
                    slack_player_data[-1]["payload"]["actions"][0]["selected_options"],
                )
            )
            # print(users_selected)

            # Emptying Global Object
            slack_player_data = []

            activate_players_post_to_slack(users_selected, num_of_team, response_url)


class SlackInitialMsg(Resource):
    def post(self):
        data = dict(request.form)

        triggerid = data["trigger_id"]

        # Start a different thread to process the post request for modal
        thread = threading.Thread(target=send_slack_modal, args=(triggerid,))
        thread.start()

        # Immediately send back empty HTTP 200 response
        return Response(status=200)


class GetTeams(Resource):
    # @login_required
    def get(self):

        global list_of_teams

        # Only Allow Authorised users to generate new team, otherwise return ucnahnged list
        Auth = request.headers.get("Authorization", "")
        if Auth[7:] == ACCESS_TOKEN:
            list_of_teams = obj.get_teams()

        elif not list_of_teams:
            list_of_teams = obj.get_teams()

        formatted_obj = {}
        for e, i in enumerate(list_of_teams):
            formatted_obj[f"TEAM {e+1}"] = i

        return formatted_obj


class AddPlayers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="player/s to add was not provided <players separated by a comma>",
            location="json",
        )
        super(AddPlayers, self).__init__()

    @login_required
    def post(self):
        args = self.reqparse.parse_args()
        # print(args["players"])

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]
        # print(players_list)

        returned_data = []
        for player in players_list:
            resp = obj.add_mode(player)
            returned_data.append(resp)

        players_ok = list(filter(lambda x: x["status"] == "ok", returned_data))

        if len(returned_data) == len(players_ok):
            players_ok = list(map(lambda x: x["name"], players_ok))
            response = ({"text": f"Users Added: {', '.join(players_ok)}"}, 201)
        else:
            players_error = list(
                filter(lambda x: x["status"] == "error", returned_data)
            )
            players_error = list(map(lambda x: x["name"], players_error))
            response = (
                {"text": f"Players already Exist: {', '.join(players_error)}"},
                409,
            )

        return response


class DeletePlayers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="player/s to delete was not provided <players separated by a comma>",
            location="json",
        )
        super(DeletePlayers, self).__init__()

    @login_required
    def delete(self):
        args = self.reqparse.parse_args()

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]

        returned_data = []
        for player in players_list:
            resp = obj.delete_mode(player)
            returned_data.append(resp)

        players_ok = list(filter(lambda x: x["status"] == "ok", returned_data))

        if len(returned_data) == len(players_ok):
            players_ok = list(map(lambda x: x["name"], players_ok))
            response = ({"text": f"Users Deleted: {', '.join(players_ok)}"}, 200)
        else:
            players_error = list(
                filter(lambda x: x["status"] == "error", returned_data)
            )
            players_error = list(map(lambda x: x["name"], players_error))
            response = (
                {"text": f"Players don't exist: {', '.join(players_error)}"},
                404,
            )

        return response


class UpdateTeamNum(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=int,
            required=True,
            help="Number of Players <int>",
            location="json",
        )
        super(UpdateTeamNum, self).__init__()

    @login_required
    def post(self):
        args = self.reqparse.parse_args()
        resp = obj.update_mode(args["data"])

        if resp["status"] == "ok":
            response = ({"text": "Team Number Updated"}, 200)

        return response


class ActivatePlayers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="Name of Players to activate <string seperated by comma> or all",
            location="json",
        )
        super(ActivatePlayers, self).__init__()

    @login_required
    def post(self):
        args = self.reqparse.parse_args()

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]

        if "All" in players_list and len(players_list) == 1:
            resp = obj.set_all_players(activate=True)
            if resp["status"] == "ok":
                response = ({"text": "All Players Activated"}, 200)
            else:
                response = ({"text": "Internal Server Error"}, 500)
        else:

            returned_data = []
            for player in players_list:
                resp = obj.activate_player(player)
                returned_data.append(resp)

            if None not in returned_data and len(returned_data) == len(players_list):
                response = ({"text": "Player/s Activated"}, 200)
            elif None in returned_data and returned_data.count(None) != len(
                players_list
            ):
                returned_data = [x for x in returned_data if x is not None]
                activated_players = list(map(lambda x: x["name"], returned_data))
                activated_players = ", ".join(activated_players)
                response = (
                    {
                        "text": f"Some Players were not activated as they don't exist. Activated Players: {activated_players}"
                    },
                    404,
                )
            else:
                response = (
                    {"text": f"No Players were activated as they don't exist"},
                    404,
                )

        return response


class DeactivatePlayers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="Name of Players to activate <string seperated by comma> or all",
            location="json",
        )
        super(DeactivatePlayers, self).__init__()

    @login_required
    def post(self):
        args = self.reqparse.parse_args()

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]

        if "All" in players_list and len(players_list) == 1:
            resp = obj.set_all_players(activate=False)
            if resp["status"] == "ok":
                response = ({"text": "All Players Deactivated"}, 200)
            else:
                response = ({"text": "Internal Server Error"}, 500)
        else:

            returned_data = []
            for player in players_list:
                resp = obj.deactivate_player(player)
                returned_data.append(resp)

            if None not in returned_data and len(returned_data) == len(players_list):
                response = ({"text": "Player/s Deactivated"}, 200)
            elif None in returned_data and returned_data.count(None) != len(
                players_list
            ):
                returned_data = [x for x in returned_data if x is not None]
                deactivated_players = list(map(lambda x: x["name"], returned_data))
                deactivated_players = ", ".join(deactivated_players)
                response = (
                    {
                        "text": f"Some Players were not deactivated as they don't exist. Deactivated Players: {deactivated_players}"
                    },
                    404,
                )
            else:
                response = (
                    {"text": f"No Players were deactivated as they don't exist"},
                    404,
                )

        return response


class AddToBalance(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="player/s to add was not provided <players separated by a comma>",
            location="json",
        )
        super(AddToBalance, self).__init__()

    @login_required
    def post(self):
        args = self.reqparse.parse_args()

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]

        returned_data = []
        for player in players_list:
            resp = obj.add_to_balance(player)
            returned_data.append(resp)

        players_ok = list(
            filter(
                lambda x: x["status"] == "ok" or x["status"] == "ok_2", returned_data
            )
        )

        if len(returned_data) == len(players_ok):
            players_ok = list(map(lambda x: x["name"], players_ok))
            response = (
                {"text": f"Users Added to Balance: {', '.join(players_ok)}"},
                201,
            )
        else:
            players_error = list(
                filter(lambda x: x["status"] == "error", returned_data)
            )
            players_error = list(map(lambda x: x["name"], players_error))
            response = (
                {"text": f"Players do not exist: {', '.join(players_error)}"},
                409,
            )

        return response


class DeleteFromBalance(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="player/s to delete was not provided <players separated by a comma>",
            location="json",
        )
        super(DeleteFromBalance, self).__init__()

    @login_required
    def delete(self):
        args = self.reqparse.parse_args()

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]

        returned_data = []
        for player in players_list:
            resp = obj.delete_from_balance(player)
            returned_data.append(resp)

        players_ok = list(filter(lambda x: x["status"] == "ok", returned_data))

        if len(returned_data) == len(players_ok):
            players_ok = list(map(lambda x: x["name"], players_ok))
            response = ({"text": f"Users Removed: {', '.join(players_ok)}"}, 200)
        else:
            players_error = list(
                filter(lambda x: x["status"] == "error", returned_data)
            )
            players_error = list(map(lambda x: x["name"], players_error))
            response = (
                {
                    "text": f"Players don't exist in balance list: {', '.join(players_error)}"
                },
                404,
            )

        return response


api.add_resource(GetTeams, "/get_teams")
api.add_resource(AddPlayers, "/add")
api.add_resource(DeletePlayers, "/delete")
api.add_resource(UpdateTeamNum, "/update_team_number")
api.add_resource(ActivatePlayers, "/activate")
api.add_resource(DeactivatePlayers, "/deactivate")
api.add_resource(AddToBalance, "/add_b")
api.add_resource(DeleteFromBalance, "/delete_b")
api.add_resource(SlackData, "/slack")
api.add_resource(SlackInitialMsg, "/mainmodal")

# api.add_resource(Baz, '/Baz', '/Baz/<string:id>')

if __name__ == "__main__":
    app.run(debug=True)
