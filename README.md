# Flask Web Service

This repo consists of the Team Generator GUI App which has been deconstructed, removing GUI related logic from the business Logic and converted into a REST API.

Endpoints exist which perform the requested operation.

Authorization is required in the form of a Bearer Token which can be set on your host machine via:

```bash
# For Linux
export TMG_API_TOKEN={xyz}

# For Windows
set TMG_API_TOKEN={xyz}
```

> A base URL of `/v1/` has been added, thus `/get_teams` is `/v1/get_teams`

`/get_teams` generates the list of teams and does not regenerate unless an authenticated GET request is made.

| EndPoint            | Method | Accepts                                        | Example                                                     |
| ------------------- | ------ | ---------------------------------------------- | ----------------------------------------------------------- |
| /get_teams          | GET    |                                                | N/A                                                         |
| /add                | POST   | \<string of users seperated by comma>          | `{"data":"Player1.Name, Player2.Name"}`                     |
| /delete             | DELETE | \<string of users seperated by comma>          | `{"data":"Player1.Name, Player2.Name"}`                     |
| /update_team_number | POST   | \<int>                                         | `{"data":2}`                                                |
| /activate           | POST   | \<string of users seperated by comma> or `All` | `{"data":"All"}` or `{"data":"Player1.Name, Player2.Name"}` |
| /deactivate         | POST   | \<string of users seperated by comma> or `All` | `{"data":"All"}` or `{"data":"Player1.Name, Player2.Name"}` |
| /add_b              | POST   | \<string of users seperated by comma>          | `{"data":"Player1.Name, Player2.Name"}`                     |
| /delete_b           | DELETE | \<string of users seperated by comma>          | `{"data":"Player1.Name, Player2.Name"}`                     |

> `/add_b` & `/delete_b` > add / delete from balance list respectively

```bash
# Example GET - No Authorisation - Same list retrieved every time
curl -X GET \
  http://localhost:5000/v1/get_teams \
  -H 'Content-Type: application/json'

# Example GET - With Authorisation - New list generated each time
curl -X GET \
  http://localhost:5000/v1/get_teams \
  -H 'Authorization: Bearer TOKEN_GOES_HERE' \
  -H 'Content-Type: application/json'

# Example POST
curl -X POST \
  http://localhost:5000/v1/add \
  -H 'Authorization: Bearer TOKEN_GOES_HERE' \
  -H 'Content-Type: application/json' \
  -d '{"data":"New.Player"}'
```

# Slack

Slack Integration has been added.

You must create an APP in Slack and setup a few things:

- Get an OAuth Access Token. It is in the form of `xoxb-000000000-000000-ABCDEFGHIJ`
- Setup a Slash Command with the request going to: `https://{WEBSITE}/v1/mainmodal`
- Setup an Interactivty Request URL: `https://{WEBSITE}/v1/slack`
  > Slack will send an HTTP POST request with information to the above URL when users interact with a shortcut or interactive component e.g Submitting data in a Modal.

Export the environment variables in your server

```bash
# For Linux
export SLACK_TOKEN=Bearer xoxb-{xyz}

# For Windows
set SLACK_TOKEN=Bearer xoxb-{xyz}
```

An example wsgi.ini file:

```bash
[uwsgi]
module = wsgi:app

env = TMG_API_TOKEN=MYTOKEN
env = SLACK_TOKEN=Bearer xoxb-SLACK-TOKEN

logto = /path_to_server/wsgi.log

enable-threads = true
master = true
processes = 5
threads = 10

socket = flsk.sock
chmod-socket = 660
vacuum = true

die-on-term = true
```

## Process

A slash command is entered by a user which sends a post request to the API server. The API server Immediately Responds back with an EMPTY HTTP 200 Response and also starts a separate thread to initiate the modal to appear.

<img src="./images/slash_command.png" alt="Image showing slash command /teams" height=180 width=500>

A `POST` request is sent to Slack with the modal object which is then displayed to a user.

<img src="./images/modal_ex1.png" alt="Modal Example" height=380 width=450>

As the user selects the different options, a `POST` request is to the API service which saves the state of the data.

<img src="./images/modal_ex2.png" alt="Modal Example" height=430 width=450>

Once the user hits the `Submit` button, a final `POST` request is sent to the API service which initiates background processing after which a response is then sent to Slack. This response appears as text in the selected Slack Channel.

<img src="./images/slack_chat.png" alt="Image Of Slack Chat" width="250" height="350">

## Slash Commands

A total of 5 slash commands can be created that reach 5 different endpoints.

For this example the `/teams` command as seen above was used along with the following commands:

<img src="./images/slash_command_ex2.png" alt="Image Of Slack Chat" width="480" height="250">

These commands correspond to the following endpoints (setup your own command to these endpoints) :

| Slash Command          | Endpoint          | Type | Usage                              |
| ---------------------- | ----------------- | ---- | ---------------------------------- |
| /teams                 | `/mainmodal`      | POST | N/A                                |
| /tmg_add               | `/slack/add`      | POST | `John.Smith, Bruce.Wayne`          |
| /tmg_delete            | `/slack/delete`   | POST | `John.Smith, Bruce.Wayne`          |
| /tmg_addtobalance      | `/slack/add_b`    | POST | `John.Smith, Bruce.Wayne`          |
| /tmg_deletefrombalance | `/slack/delete_b` | POST | `All` OR `John.Smith, Bruce.Wayne` |

The last 4 commands are sent as response type `ephemeral`, therefore they are only visible to the person who ran the command and is removed upon reload.

<img src="./images/slack_chat_ex2.png" alt="Image Of Slack Chat">
