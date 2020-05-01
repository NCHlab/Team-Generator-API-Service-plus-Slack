from flask_restful import Resource, reqparse
from flask import request
from threading import Lock
import config
import logging

logger = logging.getLogger(__name__)
mutex = Lock()
list_of_teams = []


class GetTeams(Resource):
    def get(self):

        Auth = request.headers.get("Authorization", "")
        list_of_teams = gen_teams(Auth)
        formatted_obj = format_obj(list_of_teams)

        return formatted_obj, 200


def gen_teams(Auth):

    global list_of_teams

    mutex.acquire()

    # Only Allow Authorised users to generate new team, otherwise return unchanged list
    if Auth[7:] == config.ACCESS_TOKEN:
        logger.info("Authorized user, generating teams")
        list_of_teams = config.obj.get_teams()

    elif not list_of_teams:
        logger.info("Unauthorized user, generating teams first time")
        list_of_teams = config.obj.get_teams()
    else:
        logger.info("Unauthorized user, retrieving cached data")

    mutex.release()

    return list_of_teams


def format_obj(list_of_teams):

    formatted_obj = {}
    for num, name in enumerate(list_of_teams):
        formatted_obj[f"TEAM {num+1}"] = name

    return formatted_obj


if __name__ == "__main__":
    pass
