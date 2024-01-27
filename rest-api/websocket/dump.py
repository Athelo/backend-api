from datetime import datetime


TEST_ROOMS = {
    "room1": {
        'members_count': 2,
        'members': ["Gandalf", "Admin"],
        'messages': [
            {
                "id": 1,
                "sender": "",
                "text": "Gandalf has created the chat",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        ],
        'name': "Room-1",
        'creator': "Gandalf",
        'code': "room1",
        'device_identifiers': ["device_identifier"]
    },
    "room2": {
        'members_count': 2,
        'members': ["Admin", "Gandalf"],
        'messages': [
            {
                "id": 1,
                "sender": "",
                "text": "Admin has created the chat",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        ],
        'name': "Room-2",
        'creator': "Admin",
        'code': "room2",
        'device_identifiers': ["device_identifier"]
    }
}
TEST_USERS_DUMP = {
    "Gandalf": {
        "id": 1,
        "name": "Gandalf",
        "rooms": [
            TEST_ROOMS["room1"],
            TEST_ROOMS["room2"]
        ],
    },
    "Admin": {
        "id": 2,
        "name": "Admin",
        "rooms": [
            TEST_ROOMS["room1"],
            TEST_ROOMS["room2"]
        ],
    }
}
