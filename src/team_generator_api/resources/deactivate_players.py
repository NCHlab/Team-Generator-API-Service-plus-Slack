from flask_restful import Resource, reqparse
from threading import Lock

from config import login_required
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

        players_list = args["data"].split(",")
        players_list = [x.strip().title() for x in players_list]

        if "All" in players_list and len(players_list) == 1:
            mutex.acquire()
            resp = config.obj.set_all_players(activate=False)
            mutex.release()

            if resp["status"] == "ok":
                response = ({"text": "All Players Deactivated"}, 200)
            else:
                response = ({"text": "Internal Server Error"}, 500)
        else:
            mutex.acquire()
            returned_data = []
            for player in players_list:
                resp = config.obj.deactivate_player(player)
                returned_data.append(resp)
            mutex.release()

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
