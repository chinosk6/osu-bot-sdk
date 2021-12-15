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
    all_players_are_ready = "all_players_are_ready"
    user_finished_playing = "user_finished_playing"
    host_is_changing_map = "host_is_changing_map"
    match_has_started = "match_has_started"
    match_finished = "match_finished"


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

class UserGrade(BaseModel):
    name: Optional[str]
    channel_id: Optional[str]
    is_pass: Optional[bool]
    score: Optional[int]

    def __init__(self, name="", channel_id="", is_pass=True, score=-1):
        data = {}
        if name != "":
            data["name"] = name
        if channel_id != "":
            data["channel_id"] = channel_id

        data["is_pass"] = is_pass
        data["score"] = int(score)

        super().__init__(**data)
