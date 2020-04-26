import os

# Require Token to use the API Web Service
ACCESS_TOKEN = os.environ["TMG_API_TOKEN"]

try:
    SLACK_TOKEN = os.environ["SLACK_TOKEN"]
except KeyError:
    print("SLACK_TOKEN ENVIRONMENT VARIABLE NOT SET")

list_of_teams = []
slack_player_data = []

obj = None

# print(__name__)

if __name__ == "__main__":
    pass
