PLAYER_MODAL_OBJ = {
    "trigger_id": "triggerid",
    "view": {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Team Generator"},
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":ghost: *Select Players to generate a team*",
                },
            },
            {"type": "divider"},
            {
                "block_id": "channel_to_post",
                "type": "input",
                "optional": False,
                "label": {
                    "type": "plain_text",
                    "text": "Select a channel to post the result on",
                },
                "element": {
                    "action_id": "send_to_channel",
                    "type": "channels_select",
                    "response_url_enabled": True,
                },
            },
            {
                "type": "input",
                "block_id": "num_of_teams",
                "label": {"type": "plain_text", "text": "Select Number Of Teams",},
                "element": {
                    "type": "static_select",
                    "action_id": "num_of_teams_action",
                    "initial_option": {
                        "text": {"type": "plain_text", "text": "2"},
                        "value": "2",
                    },
                    "options": [
                        {"text": {"type": "plain_text", "text": "1"}, "value": "1",},
                        {"text": {"type": "plain_text", "text": "2"}, "value": "2",},
                        {"text": {"type": "plain_text", "text": "3"}, "value": "3",},
                        {"text": {"type": "plain_text", "text": "4"}, "value": "4",},
                        {"text": {"type": "plain_text", "text": "5"}, "value": "5",},
                        {"text": {"type": "plain_text", "text": "6"}, "value": "6",},
                    ],
                },
            },
            {
                "type": "section",
                "block_id": "player_list",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Select players to generate teams*",
                },
                "accessory": {
                    "type": "multi_static_select",
                    "placeholder": {"type": "plain_text", "text": "Select Players"},
                    "action_id": "player_list_action",
                    "options": [],
                },
            },
        ],
    },
}

INPUT_BLOCK = {
    "type": "input",
    "block_id": "player_list",
    "label": {"type": "plain_text", "text": "Players", "emoji": True,},
    "element": {
        "type": "checkboxes",
        "action_id": "player_list_action",
        "options": [],
    },
}

PLAYER_CHECKBOX = {
    "text": {"type": "plain_text", "text": ""},
    "value": "",
}
