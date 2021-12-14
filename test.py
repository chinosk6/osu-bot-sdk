import osu_irc_sdk
from osu_irc_sdk import models

bot = osu_irc_sdk.OsuBot("", "", debug=True)  # see: https://osu.ppy.sh/p/irc


@bot.receiver(models.Codes.someone_joined_room)
def join(event: models.Message):
    print(f"{event.name} 加入了房间: {event.message}")


@bot.receiver(models.Codes.private_message)
def pmessage(event: models.Message):
    print(f"收到私聊: {event.name} - {event.message}")
    bot.api.send_private_message(event.name, f"我是复读机: {event.message}")


@bot.receiver(models.Codes.channel_message)
def pmessage(event: models.Message):
    print(f"收到来自 {event.channel_id} 频道:{event.name} - {event.message}")
    bot.api.send_private_message(event.channel_id, f"我是复读机: {event.message}")

@bot.receiver(models.Codes.someone_joined_slot)
def join_slot(event: models.Message):
    print(f"{event.name} 加入了 {event.channel_id} 的 {event.message} 号位")
    if bot.name == event.name:
        bot.api.room_set_host(event.channel_id, event.name)


@bot.receiver(models.Codes.someone_changed_slot)
def join_slot(event: models.Message):
    print(f"{event.name} 在 {event.channel_id} 中, 移动到了 {event.message} 号位")


@bot.receiver(models.Codes.run_after_start)
def rrr():
    # bot.api.room_set_passwd("#mp_95224191", "114514")
    print("开房间", bot.api.room_create("chinosk's game", "114514", True, 4))
    # print("开房间", bot.api.room_create("chinosk's game2", "114514", True, 4))
    # print("开房间", bot.api.room_create("chinosk's game3", "114514", True, 4))
    # print("开房间", bot.api.room_create("chinosk's game4", "114514", True, 4))
    # print("开房间", bot.api.room_create("chinosk's game5", "114514", True, 4))


@bot.receiver(models.Codes.changed_song)
def cs(event: models.Message):
    print(f"房间: {event.channel_id} 曲目更改为: {event.message}")

@bot.receiver(models.Codes.someone_left_room)
def lft(event: models.Message):
    print(f"玩家: {event.name} 离开了房间: {event.channel_id}")

@bot.receiver(models.Codes.changed_host)
def chst(event: models.Message):
    print(f"玩家: {event.name} 成为了 {event.channel_id} 的房主")

@bot.receiver(models.Codes.match_closed)
def chst(event: models.Message):
    print(f"房间: {event.channel_id} 被关闭")


bot.strat()

