from flask_restful import Resource, reqparse
from threading import Lock
import ast
import logging

from config import login_required
import config

logger = logging.getLogger(__name__)
mutex = Lock()


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

        try:
            players_data = ast.literal_eval(args["data"])
            if isinstance(players_data, list):
                players_list = [x.strip().title() for x in players_data]
            logger.warning(f"Received str repr of a list of player data {args['data']}")
        except:
            logger.debug(f"Processing datatype: {type(args['data'])}")
            players_list = args["data"].split(",")
            players_list = [x.strip().title() for x in players_list]

        mutex.acquire()

        returned_data = []
        for player in players_list:
            resp = config.obj.delete_mode(player)
            returned_data.append(resp)

        mutex.release()
        logger.debug(f"Returned Data: {returned_data}")

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
