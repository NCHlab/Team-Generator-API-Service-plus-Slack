# Flask Web Service

The Team Generator App has been deconstructed, removing GUI related logic from the business Logic.

Endpoints exist which perform the requested operation.

Authorization is required in the form of a Bearer Token which can be set on your host machine via:

```bash
# For Linux
export TMG_API_TOKEN={xyz}

# For Windows
set TMG_API_TOKEN={xyz}
```

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

<img src="./images/slack_chat.png" alt="Image Of Slack Chat" width="404" height="330">
