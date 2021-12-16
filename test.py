import osu_irc_sdk
from osu_irc_sdk import models

_proxy = osu_irc_sdk.OsuIrcProxy(osu_irc_sdk.OsuIrcProxy.PROXY_TYPE_SOCKS5, "127.0.0.1", 10086)
bot = osu_irc_sdk.OsuBot("", "", debug=True, proxy=_proxy)  # see: https://osu.ppy.sh/p/irc


@bot.receiver(models.Codes.run_after_start)
def rrr():
    # bot.logger("开房间", bot.api.room_create("aaa's game", "114514", True, 4), test=True)
    pass

@bot.receiver(models.Codes.someone_joined_room)
def join(event: models.Message):
    bot.logger(f"{event.name} 加入了房间: {event.message}", test=True)


@bot.receiver(models.Codes.private_message)
def pmessage(event: models.Message):
    bot.logger(f"收到私聊: {event.name} - {event.message}")
    # bot.api.send_private_message(event.name, f"我是复读机: {event.message}")


@bot.receiver(models.Codes.channel_message)
def cmessage(event: models.Message):
    bot.logger(f"收到来自 {event.channel_id} 频道:{event.name} - {event.message}")
    # bot.api.send_private_message(event.channel_id, f"我是复读机: {event.message}")

@bot.receiver(models.Codes.someone_joined_slot)
def join_slot(event: models.Message):
    bot.logger(f"{event.name} 加入了 {event.channel_id} 的 {event.message} 号位", test=True)
    if bot.name == event.name:
        bot.api.room_set_host(event.channel_id, event.name)


@bot.receiver(models.Codes.someone_changed_slot)
def change_slot(event: models.Message):
    bot.logger(f"{event.name} 在 {event.channel_id} 中, 移动到了 {event.message} 号位", test=True)


@bot.receiver(models.Codes.changed_song)
def cs(event: models.Message):
    bot.logger(f"房间: {event.channel_id} 曲目更改为: {event.message}", test=True)

@bot.receiver(models.Codes.someone_left_room)
def lft(event: models.Message):
    bot.logger(f"玩家: {event.name} 离开了房间: {event.channel_id}", test=True)

@bot.receiver(models.Codes.changed_host)
def chst(event: models.Message):
    bot.logger(f"玩家: {event.name} 成为了 {event.channel_id} 的房主", test=True)

@bot.receiver(models.Codes.match_closed)
def clst(event: models.Message):
    bot.logger(f"房间: {event.channel_id} 被关闭", test=True)

@bot.receiver(models.Codes.all_players_are_ready)
def rdy(event: models.Message):
    bot.logger(f"房间: {event.channel_id} 所有成员已准备就绪", test=True)

@bot.receiver(models.Codes.user_finished_playing)
def fsh(event: models.UserGrade):
    bot.logger(f"房间: {event.channel_id} 玩家: {event.name} 已完成游戏, 分数: {event.score}, 是否通过: {event.is_pass}",
               test=True)

@bot.receiver(models.Codes.host_is_changing_map)
def cmp(event: models.Message):
    bot.logger(f"房间: {event.channel_id} 正在修改地图", test=True)

@bot.receiver(models.Codes.match_has_started)
def stt(event: models.Message):
    bot.logger(f"房间: {event.channel_id} 开始游戏", test=True)

@bot.receiver(models.Codes.match_finished)
def stt(event: models.Message):
    bot.logger(f"房间: {event.channel_id} 所有人已完成游戏", test=True)


bot.strat()

