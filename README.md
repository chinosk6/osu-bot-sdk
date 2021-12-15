# osu-bot-sdk
- an OSU! bot sdk based on IRC



# Start!

- The following is an example of event triggering

```python
import osu_irc_sdk
from osu_irc_sdk import models

bot = osu_irc_sdk.OsuBot("your name", "your password", debug=True)  # see: https://osu.ppy.sh/p/irc

@bot.receiver(models.Codes.run_after_start)
def rrr():
    # Create a game room immediately after startup
    bot.logger("create room", bot.api.room_create("my test room", "114514", True, 4), test=True)


@bot.receiver(models.Codes.someone_joined_room)
def join(event: models.Message):
    bot.logger(f"{event.name} joined: {event.message}", test=True)


@bot.receiver(models.Codes.private_message)
def pmessage(event: models.Message):
    bot.logger(f"Get private chat: {event.name} - {event.message}")
    # bot.api.send_private_message(event.name, f"我是复读机: {event.message}")


@bot.receiver(models.Codes.channel_message)
def cmessage(event: models.Message):
    bot.logger(f"Message from {event.channel_id} :{event.name} - {event.message}")
    # bot.api.send_private_message(event.channel_id, f"{event.message}")

@bot.receiver(models.Codes.someone_joined_slot)
def join_slot(event: models.Message):
    bot.logger(f"{event.name} joined {event.channel_id} - {event.message} slot", test=True)
    if bot.name == event.name:
        bot.api.room_set_host(event.channel_id, event.name)


@bot.receiver(models.Codes.someone_changed_slot)
def change_slot(event: models.Message):
    bot.logger(f"{event.name} in {event.channel_id}, moved to {event.message} slot", test=True)


@bot.receiver(models.Codes.changed_song)
def cs(event: models.Message):
    bot.logger(f"room: {event.channel_id} changed song: {event.message}", test=True)

@bot.receiver(models.Codes.someone_left_room)
def lft(event: models.Message):
    bot.logger(f"{event.name} left: {event.channel_id}", test=True)

@bot.receiver(models.Codes.changed_host)
def chst(event: models.Message):
    bot.logger(f"{event.name} became the host of {event.channel_id}", test=True)

@bot.receiver(models.Codes.match_closed)
def clst(event: models.Message):
    bot.logger(f"room {event.channel_id} closed", test=True)

@bot.receiver(models.Codes.all_players_are_ready)
def rdy(event: models.Message):
    bot.logger(f"room: {event.channel_id} all players are ready", test=True)

@bot.receiver(models.Codes.user_finished_playing)
def fsh(event: models.UserGrade):
    bot.logger(f"room: {event.channel_id} player: {event.name} completed game, score: {event.score}, is_pass: {event.is_pass}",
               test=True)

@bot.receiver(models.Codes.host_is_changing_map)
def cmp(event: models.Message):
    bot.logger(f"room: {event.channel_id} is revising map", test=True)

@bot.receiver(models.Codes.match_has_started)
def stt(event: models.Message):
    bot.logger(f"room: {event.channel_id} started the match", test=True)

@bot.receiver(models.Codes.match_finished)
def stf(event: models.Message):
    bot.logger(f"room: {event.channel_id} - match has finished", test=True)


bot.strat()
```



# Events

- `models.Codes`

```python
run_after_start  # This is a special event that will be executed immediately after successfully connecting to Bancho.
channel_message  # messages from room
private_message  # private message
someone_joined_room  # triggered only when a room is created
someone_joined_slot  # someone joined room
someone_changed_slot
changed_song
changed_host
someone_left_room
match_closed  # room closed
all_players_are_ready
user_finished_playing  # someone finished playing
host_is_changing_map
match_has_started
match_finished  # all players complete
```



# API

- `OsuBot.api`

```python
send_private_message(username, message)
send_channel_message(room_id, message)  # commands are also ok
room_create(room_name, passwd="", free_mods=False, max_member="")  # it will return the room_id
room_set_passwd(room_id, passwd)
room_set_max_member(room_id, max_member)
room_set_host(room_id, host_name)
room_set_mods(room_id, mods)
room_strat_game(room_id)
room_change_map(room_id, map_id, mode="")  # mode:0/1/2/3
```

