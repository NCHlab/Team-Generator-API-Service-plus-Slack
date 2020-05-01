from flask_restful import Resource, reqparse
from threading import Lock

from config import login_required, parse_player
import config

mutex = Lock()


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
        players_list = parse_player(args["data"])

        if "All" in players_list and len(players_list) == 1:
            player_status = deactivate_all()
            response = process_all_output(player_status)

        else:
            player_status = deactivate_players(players_list)
            response = process_output(player_status, players_list)

        return response


def deactivate_all():

    mutex.acquire()
    player_status = config.obj.set_all_players(activate=False)
    mutex.release()

    return player_status


def process_all_output(resp):

    if resp["status"] == "ok":
        response = ({"text": "All Players Deactivated"}, 200)
    else:
        response = ({"text": "Internal Server Error"}, 500)

    return response


def deactivate_players(players_list):

    mutex.acquire()
    player_status = []
    for player in players_list:
        resp = config.obj.deactivate_player(player)
        player_status.append(resp)
    mutex.release()

    return player_status


def process_output(player_status, players_list):

    if None not in player_status and len(player_status) == len(players_list):
        response = ({"text": "Player/s Deactivated"}, 200)

    elif None in player_status and player_status.count(None) != len(players_list):

        player_status = [x for x in player_status if x is not None]
        deactivated_players = list(map(lambda x: x["name"], player_status))
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
