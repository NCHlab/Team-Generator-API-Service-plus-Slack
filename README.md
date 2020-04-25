# Flask Web Serice

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
