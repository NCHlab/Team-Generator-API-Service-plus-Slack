from flask_restful import Resource, reqparse
from threading import Lock
import ast
import logging

from config import login_required, parse_player
import config

logger = logging.getLogger(__name__)
mutex = Lock()


class AddPlayers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "data",
            type=str,
            required=True,
            help="player/s to add was not provided <players separated by a comma>, send data with content type json",
            location="json",
        )
        super(AddPlayers, self).__init__()

    @login_required
    def post(self):

        args = self.reqparse.parse_args()

        try:
            players_data = ast.literal_eval(args["data"])
            if isinstance(players_data, list):
                players_list = [player.strip().title() for player in players_data]
            logger.warning(f"Received str repr of a list of player data {args['data']}")
        except:
            logger.debug(f"Processing datatype: {type(args['data'])}")
            players_list = parse_player(args["data"])

        player_status = add_player(players_list)
        response = process_output(player_status)

        return response


def add_player(players_list):

    mutex.acquire()
    player_status = []
    for player in players_list:
        resp = config.obj.add_mode(player)
        player_status.append(resp)

    mutex.release()
    logger.debug(f"Returned Data: {player_status}")

    return player_status


def process_output(player_status):
    players_ok = list(filter(lambda x: x["status"] == "ok", player_status))

    if len(player_status) == len(players_ok):
        players_ok = list(map(lambda x: x["name"], players_ok))
        response = ({"text": f"Users Added: {', '.join(players_ok)}"}, 201)
    else:
        players_error = list(filter(lambda x: x["status"] == "error", player_status))
        players_error = list(map(lambda x: x["name"], players_error))
        response = (
            {"text": f"Players already Exist: {', '.join(players_error)}"},
            409,
        )

    return response
