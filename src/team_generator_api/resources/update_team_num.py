from flask_restful import Resource, reqparse
from threading import Lock
import config

mutex = Lock()


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

    @config.login_required
    def post(self):
        args = self.reqparse.parse_args()

        mutex.acquire()
        resp = config.obj.update_mode(args["data"])
        mutex.release()

        if resp["status"] == "ok":
            response = ({"text": "Team Number Updated"}, 200)

        return response
