from flask_restful import Resource, reqparse
from threading import Lock

from config import login_required
import config

mutex = Lock()


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

        mutex.acquire()

        returned_data = []
        for player in players_list:
            resp = config.obj.add_to_balance(player)
            returned_data.append(resp)

        mutex.release()

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
