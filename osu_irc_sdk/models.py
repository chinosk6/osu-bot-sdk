from pydantic import BaseModel
from typing import Optional


class Codes:
    channel_message = "channel_message"
    private_message = "private_message"
    someone_joined_room = "someone_joined_room"
    someone_joined_slot = "someone_joined_slot"
    someone_changed_slot = "someone_changed_slot"
    run_after_start = "run_after_start"
    changed_song = "changed_song"
    changed_host = "changed_host"
    someone_left_room = "someone_left_room"
    match_closed = "match_closed"


class Message(BaseModel):
    name: Optional[str]
    channel_id: Optional[str]
    message: Optional[str]


    def __init__(self, name="", message="", channel_id=""):
        data = {}
        if name != "":
            data["name"] = name
        if message != "":
            data["message"] = message
        if channel_id != "":
            data["channel_id"] = channel_id

        super().__init__(**data)
