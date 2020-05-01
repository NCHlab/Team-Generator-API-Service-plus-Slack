from flask_restful import Resource, reqparse
from threading import Lock

from config import login_required, parse_player
import config

mutex = Lock()


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
        players_list = parse_player(args["data"])
        player_status = delete_from_balance(players_list)
        response = process_output(player_status)

        return response


def delete_from_balance(players_list):

    mutex.acquire()

    player_status = []
    for player in players_list:
        resp = config.obj.delete_from_balance(player)
        player_status.append(resp)

    mutex.release()

    return player_status


def process_output(player_status):

    players_ok = list(filter(lambda x: x["status"] == "ok", player_status))

    if len(player_status) == len(players_ok):
        players_ok = list(map(lambda x: x["name"], players_ok))
        response = ({"text": f"Users Removed: {', '.join(players_ok)}"}, 200)
    else:
        players_error = list(filter(lambda x: x["status"] == "error", player_status))
        players_error = list(map(lambda x: x["name"], players_error))
        response = (
            {
                "text": f"Players don't exist in balance list: {', '.join(players_error)}"
            },
            404,
        )

    return response
