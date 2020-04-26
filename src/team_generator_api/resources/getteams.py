from flask_restful import Api, Resource, reqparse
from flask import Flask, Blueprint, request, Response
import config

# get_teams_api = Blueprint("GetTeams", __name__)


class GetTeams(Resource):
    # @login_required
    def get(self):

        # global list_of_teams

        # Only Allow Authorised users to generate new team, otherwise return ucnahnged list
        Auth = request.headers.get("Authorization", "")
        if Auth[7:] == config.ACCESS_TOKEN:
            config.list_of_teams = config.obj.get_teams()

        elif not config.list_of_teams:
            config.list_of_teams = config.obj.get_teams()

        formatted_obj = {}
        for e, i in enumerate(config.list_of_teams):
            formatted_obj[f"TEAM {e+1}"] = i

        return formatted_obj


if __name__ == "__main__":
    pass
