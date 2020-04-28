from flask_restful import Resource, reqparse
from flask import request
from threading import Lock
import config

mutex = Lock()
list_of_teams = []


class GetTeams(Resource):
    def get(self):

        global list_of_teams

        Auth = request.headers.get("Authorization", "")
        mutex.acquire()

        # Only Allow Authorised users to generate new team, otherwise return unchanged list
        if Auth[7:] == config.ACCESS_TOKEN:
            list_of_teams = config.obj.get_teams()

        elif not list_of_teams:
            list_of_teams = config.obj.get_teams()

        mutex.release()

        formatted_obj = {}
        for e, i in enumerate(list_of_teams):
            formatted_obj[f"TEAM {e+1}"] = i

        return formatted_obj


if __name__ == "__main__":
    pass
