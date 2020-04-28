from flask_restful import Api
from flask import Flask, Blueprint

from generic_gen_teams import App
import config

from resources.get_teams import GetTeams
from resources.add_players import AddPlayers
from resources.delete_players import DeletePlayers
from resources.update_team_num import UpdateTeamNum
from resources.activate_players import ActivatePlayers
from resources.deactivate_players import DeactivatePlayers
from resources.add_to_balance import AddToBalance
from resources.delete_from_balance import DeleteFromBalance

from slack_resources.tmg_modal import SlackInitialMsg
from slack_resources.process_slack_data import SlackData

app = Flask(__name__)

blueprint = Blueprint("api", __name__, url_prefix="/v1")
api = Api(blueprint)
app.register_blueprint(blueprint)

config.obj = App()


api.add_resource(GetTeams, "/get_teams")
api.add_resource(AddPlayers, "/add")
api.add_resource(DeletePlayers, "/delete")
api.add_resource(UpdateTeamNum, "/update_team_number")
api.add_resource(ActivatePlayers, "/activate")
api.add_resource(DeactivatePlayers, "/deactivate")
api.add_resource(AddToBalance, "/add_b")
api.add_resource(DeleteFromBalance, "/delete_b")
api.add_resource(SlackData, "/slack")
api.add_resource(SlackInitialMsg, "/mainmodal")

# api.add_resource(Baz, '/Baz', '/Baz/<string:id>')

if __name__ == "__main__":
    app.run(debug=True)
