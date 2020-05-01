import os
import json
import random
from sys import exit
import requests

global_list = []


class App:
    def __init__(self):
        self.initialise_data()

    def initialise_data(self):

        self.load_data()
        self.generate_player()

    def about_me(self):
        return ({"message": "Author: Nayam Chowdhury"}, 200)

    def load_data(self):

        try:
            with open("./team_list.json", "r") as wr:
                self.team_data = json.load(wr)
        except json.decoder.JSONDecodeError:
            response = "y"
            file_error(response)
            with open("./team_list.json", "r") as wr:
                self.team_data = json.load(wr)

        # Format the data into Capital Letter for first letter: User.Smith
        self.team_data["names"] = list(
            map(lambda x: x.title(), self.team_data["names"])
        )
        self.team_data["balance"] = list(
            map(lambda x: x.title(), self.team_data["balance"])
        )

        self.team_list = self.team_data.get("names", [])
        self.team_list_balance = self.team_data.get("balance", [])
        self.num_of_team = (
            self.team_data.get("numOfTeam", 2)
            if type(self.team_data["numOfTeam"]) == int
            else int(self.team_data.get("numOfTeam", 2))
        )

    def generate_player(self):
        self.num_of_players = len(self.team_list)
        self.player_obj = list()

        for i in range(self.num_of_players):
            self.player_obj.append(Person(self.team_list[i]))
        return self.player_obj

    def set_slack_key(self):

        os.environ["SLACK_KEY"] = self.slack_key_field
        return "Key Set"

    def process_for_slack(self):
        if hasattr(self, "shuffled_teams"):
            response = send_to_slack(self.shuffled_teams)
        else:
            response = ({"text": "Failure, self has no attr: shuffled_teams"}, 404)

        return response

    def get_teams(self):
        self.shuffled_teams = shuffle_teams(
            global_list, self.num_of_team, self.team_list_balance
        )

        return self.shuffled_teams

    def set_all_players(self, activate=True):

        if activate:
            for i in self.player_obj:
                i.activate_player()
            return {"status": "ok", "message": "All Players Activated"}
        else:
            for i in self.player_obj:
                i.deactivate_player()
            return {"status": "ok", "message": "All Players Deactivated"}

    def deactivate_player(self, name):
        for i in self.player_obj:
            if i.name == name:
                i.deactivate_player()
                return {
                    "status": "ok",
                    "message": "Player Deactivated",
                    "name": f"{name.title()}",
                }

    def activate_player(self, name):
        for i in self.player_obj:
            if i.name == name:
                i.activate_player()
                return {
                    "status": "ok",
                    "message": "Player Activated",
                    "name": f"{name.title()}",
                }

    def add_mode(self, name):

        data = json_local_load()
        data["names"] = list(map(lambda x: x.title(), data["names"]))

        if name.title() in data["names"]:
            response = {
                "status": "error",
                "message": "Duplicate Error, Name Taken",
                "name": f"{name.title()}",
            }
        elif name:
            data["names"].append(name.title())

            json_local_write(data)
            self.refresh_all_data(data)

            response = {
                "status": "ok",
                "message": "Player Added",
                "name": f"{name.title()}",
            }

        return response

    def delete_mode(self, name):

        data = json_local_load()
        data["names"] = list(map(lambda x: x.title(), data["names"]))

        if name and name.title() in data["names"]:
            data["names"].remove(name.title())

            json_local_write(data)
            self.refresh_all_data(data)

            response = {
                "status": "ok",
                "message": "Player Deleted",
                "name": f"{name.title()}",
            }
        else:
            response = {
                "status": "error",
                "message": "Delete Failed. Name not in List",
                "name": f"{name.title()}",
            }

        return response

    def update_mode(self, num):
        data = json_local_load()

        self.num_of_team = num
        data["numOfTeam"] = self.num_of_team
        json_local_write(data)

        response = {"status": "ok", "message": "Team Number Updated"}

        return response

    def refresh_all_data(self, data):

        for i in self.player_obj:
            if i.user_in_globallist():
                i.deactivate_player()

        self.team_list = data["names"]
        del self.player_obj
        self.generate_player()

    def add_to_balance(self, name):
        data = json_local_load()
        data["balance"] = list(map(lambda x: x.title(), data["balance"]))
        data["names"] = list(map(lambda x: x.title(), data["names"]))

        if name.title() in data["balance"]:
            response = {
                "status": "ok_2",
                "message": "Player already in list",
                "name": f"{name.title()}",
            }
        elif name and name.title() in data["names"]:
            data["balance"].append(name.title())

            json_local_write(data)
            self.refresh_all_data(data)

            response = {
                "status": "ok",
                "message": "Player Added to balance list",
                "name": f"{name.title()}",
            }
        else:
            response = {
                "status": "error",
                "message": "Player does not exist. Add to players first",
                "name": f"{name.title()}",
            }

        return response

    def delete_from_balance(self, name):

        data = json_local_load()
        data["balance"] = list(map(lambda x: x.title(), data["balance"]))

        if name and name.title() in data["balance"]:
            data["balance"].remove(name.title())

            json_local_write(data)
            self.refresh_all_data(data)

            response = {
                "status": "ok",
                "message": "Player Deleted from balance list",
                "name": f"{name.title()}",
            }
        else:
            response = {
                "status": "error",
                "message": "Delete Failed. Name not in balance List",
                "name": f"{name.title()}",
            }

        return response

    def delete_all_from_balance(self):

        data = json_local_load()
        data["balance"] = []
        json_local_write(data)
        self.refresh_all_data(data)

        response = {"status": "ok", "message": "All Players deleted from balance"}
        return response


class Person:
    def __init__(self, name):

        self.name = name
        self.check_active()

    def check_active(self):
        if self.name in global_list:
            self.deactivate_player()
        else:
            self.activate_player()

    def activate_player(self):
        if self.name not in global_list:
            global_list.append(self.name)

    def deactivate_player(self):
        if self.name in global_list:
            global_list.remove(self.name)

    def user_in_globallist(self):
        return self.name in global_list


def split_list(seq, size):
    return (seq[i::size] for i in range(size))


def shuffle_teams(data, num_of_team, players_to_balance):

    # Create copy to not affect global / class instance
    data = data.copy()
    players_to_balance = players_to_balance.copy()

    # Ensure Players are selected
    if players_to_balance and data:

        temp_list = []

        for player in players_to_balance:
            # Remove duplicates from list
            if player in data:
                data.remove(player)
            else:
                # Save to remove from balance list
                temp_list.append(player)

        # Remove from playing since they arent in data
        for player in temp_list:
            players_to_balance.remove(player)

        random.shuffle(data)
        teams = list(split_list(data, num_of_team))

        random.shuffle(players_to_balance)
        teams_balanced = list(split_list(players_to_balance, num_of_team))

        # Sorting to try to distribute players fairly when re-combined
        teams.sort(key=len, reverse=False)
        teams_balanced.sort(key=len, reverse=True)

        # Add balanced players back into team
        # As balanced players added to end, Shuffling to make GUI randomize list
        for i in range(num_of_team):
            teams[i] += teams_balanced[i]
            random.shuffle(teams[i])

    else:
        random.shuffle(data)
        teams = list(split_list(data, num_of_team))

    return teams


def json_local_load(*args):

    if args:
        file_path = args[0]
        json_file = open(file_path, "r")
    else:
        json_file = open("team_list.json", "r")

    data = json.load(json_file)
    json_file.close()

    return data


def json_local_write(data):
    json_file = open("team_list.json", "w+")
    json_file.write(json.dumps(data, indent=4))
    json_file.close()


def create_new_jsonfile(*args):
    with open("team_list.json", "w") as write_file:
        json.dump({"names": [], "numOfTeam": 2, "balance": []}, write_file, indent=4)

    if args:
        obj.refresh_ui({"names": [], "numOfTeam": 2, "balance": []})
        obj.team_options()


def file_error(response):

    if response:
        create_new_jsonfile()
    else:
        exit(0)


def send_to_slack(data):
    try:
        slack_key = os.environ["SLACK_KEY"]
    except KeyError:
        return "Fail"

    url = "https://hooks.slack.com/services/" + slack_key
    response = []

    for num, players in enumerate(data):

        text = ",\n ".join(players)
        post_obj = {"text": f"TEAM {num+1}\n {text}"}

        myobj = json.dumps(post_obj)
        resp = requests.post(url, data=myobj)

        response.append(resp.text)

    return response


if __name__ == "__main__":

    if not os.path.exists("team_list.json"):
        response = input("File Doesn't Exist, Create Now?")
        if response == "y":
            file_error(response)

    obj = App()
