from .ws import OsuIrc
from . import models
import typing as t
from threading import Thread
import re


def gettext_between(text: str, before: str, after: str, is_include=False) -> str:  # 取出中间文本
    """
    取中间文本
    :param text: 原文本
    :param before: 前面文本
    :param after: 后面文本
    :param is_include: 是否取出标识文本
    :return: 操作后的文本
    """
    b_index = text.find(before)

    if (b_index == -1):
        b_index = 0
    else:
        b_index += len(before)
    af_index = text.find(after, b_index)
    if (af_index == -1):
        af_index = len(text)
    rettext = text[b_index: af_index]
    if is_include:
        rettext = before + rettext + after
    return (rettext)


class OsuBot(OsuIrc):
    def __init__(self, name: str, passwd: str, debug=False):
        super().__init__(name.replace(' ', '_').lower(), passwd, debug=debug)

        self.event_channel_message = []  # 房间消息
        self.event_private_message = []  # 私聊消息
        self.event_someone_joined_room = []  # 加入房间(仅创建房间时同步触发)
        self.event_someone_change_slot = []  # 有人换位
        self.event_someone_joined_slot = []  # 加入房间某位置(新玩家加入)
        self.event_room_changed_song = []  # 改歌曲
        self.event_room_changed_host = []  # 换房主
        self.event_someone_left_room = []  # 有人离开房间
        self.event_match_closed = []  # 房间关闭
        self.event_all_players_are_ready = []  # 所有人准备就绪
        self.event_user_finished_playing = []  # 有人完成曲目
        self.event_host_is_changing_map = []  # 房主开始修改地图
        self.event_match_has_started = []  # 游戏开始
        self.event_match_finished = []  # 所有人完成游戏

        self.run_after_start = []

        self.waiting_room = {}

        self.api = BotApi(self)

    def receiver(self, reg_type: str):
        def reg(func: t.Callable):
            def _appender(fs: t.List):
                fs.append(func)

            if reg_type == models.Codes.channel_message:
                _appender(self.event_channel_message)
            if reg_type == models.Codes.private_message:
                _appender(self.event_private_message)
            if reg_type == models.Codes.someone_joined_room:
                _appender(self.event_someone_joined_room)
            if reg_type == models.Codes.run_after_start:
                _appender(self.run_after_start)
            if reg_type == models.Codes.someone_joined_slot:
                _appender(self.event_someone_joined_slot)
            if reg_type == models.Codes.someone_changed_slot:
                _appender(self.event_someone_change_slot)
            if reg_type == models.Codes.changed_song:
                _appender(self.event_room_changed_song)
            if reg_type == models.Codes.changed_host:
                _appender(self.event_room_changed_host)
            if reg_type == models.Codes.someone_left_room:
                _appender(self.event_someone_left_room)
            if reg_type == models.Codes.match_closed:
                _appender(self.event_match_closed)
            if reg_type == models.Codes.all_players_are_ready:
                _appender(self.event_all_players_are_ready)
            if reg_type == models.Codes.user_finished_playing:
                _appender(self.event_user_finished_playing)
            if reg_type == models.Codes.host_is_changing_map:
                _appender(self.event_host_is_changing_map)
            if reg_type == models.Codes.match_has_started:
                _appender(self.event_match_has_started)
            if reg_type == models.Codes.match_finished:
                _appender(self.event_match_finished)

        return reg

    @staticmethod
    def call_func(funcs: t.List, *args, **kwargs):
        for func in funcs:
            _t = Thread(target=func, args=args, kwargs=kwargs)
            _t.start()

    def strat(self):
        self.connect()
        self.call_func(self.run_after_start)

        while True:
            for line in self.receive().split('\n'):
                line = line.strip()
                # print(line)

                if line == "ping cho.ppy.sh":
                    self.send("PONG cho.ppy.sh")
                    continue

                if f"!cho@ppy.sh privmsg {self.name} :" in line:  # 私聊消息事件
                    name = line[1: line.find("!")]
                    msg = line[line.find(f'!cho@ppy.sh privmsg {self.name} :') +
                               len(f"!cho@ppy.sh privmsg {self.name} :"):]
                    if name != "banchobot":
                        self.call_func(self.event_private_message, models.Message(name, msg))
                    else:
                        self.logger(f"Bancho: {msg}", debug=True)

                        if "created the tournament match" in msg:  # 创建房间
                            left_msg = msg[len("created the tournament match"):].strip()
                            room_url = re.findall("https://osu\\.ppy\\.sh/mp/\\d*", left_msg)
                            if room_url:
                                room_url = room_url[0]
                                room_id = "#mp_" + room_url[len("https://osu.ppy.sh/mp/"):].strip()
                                room_name = left_msg[len(room_url):].strip()
                                if room_name in self.waiting_room:
                                    self.waiting_room[room_name] = room_id

                elif "!cho@ppy.sh privmsg" in line:
                    name = line[1: line.find("!")]
                    msg = line[line.find(":", 2) + 1:]
                    channel_id = gettext_between(line, "cho@ppy.sh privmsg ", " :").strip()

                    if name == "banchobot":
                        self.logger(f"[Bancho] in {channel_id}: {msg}", debug=True)

                        if "beatmap changed to" in msg:
                            _msg = msg[len("beatmap changed to"):].strip()
                            self.call_func(self.event_room_changed_song, models.Message("", _msg, channel_id))

                        elif "joined in slot" in msg:
                            u_name = msg[:msg.find("joined in slot")].strip()
                            slot = msg[msg.find("joined in slot") + len("joined in slot"):].strip()
                            slot = slot[:-1] if slot.endswith(".") else slot
                            self.call_func(self.event_someone_joined_slot, models.Message(u_name, slot, channel_id))

                        elif "moved to slot" in msg:
                            u_name = msg[:msg.find("moved to slot")].strip()
                            slot = msg[msg.find("moved to slot") + len("moved to slot"):].strip()
                            slot = slot[:-1] if slot.endswith(".") else slot
                            self.call_func(self.event_someone_change_slot, models.Message(u_name, slot, channel_id))

                        elif "left the game" in msg:
                            u_name = msg[:msg.find("left the game")].strip()
                            self.call_func(self.event_someone_left_room,
                                           models.Message(u_name, f"{u_name} left {channel_id}", channel_id))

                        elif "became the host" in msg:
                            u_name = msg[:msg.find("became the host")].strip()
                            self.call_func(self.event_room_changed_host, models.Message(u_name, msg, channel_id))

                        elif "finished playing" in msg:
                            uname = msg[:msg.find("finished playing")].strip()
                            _score = gettext_between(msg, "score: ", ", ").strip()

                            _st = f"finished playing (score: {_score}, "
                            pass_str = gettext_between(msg, _st, ").").strip()

                            self.call_func(self.event_user_finished_playing,
                                           models.UserGrade(uname, channel_id, True if pass_str == "passed" else False,
                                                            _score))

                        elif msg == "host is changing map...":
                            self.call_func(self.event_host_is_changing_map, models.Message("", msg, channel_id))

                        elif msg == "the match has started!":
                            self.call_func(self.event_match_has_started, models.Message("", msg, channel_id))

                        elif msg == "the match has finished!":
                            self.call_func(self.event_match_finished, models.Message("", msg, channel_id))

                        elif msg == "closed the match":
                            self.call_func(self.event_match_closed, models.Message("", msg, channel_id))

                        elif "all players are ready" in msg:
                            self.call_func(self.event_all_players_are_ready, models.Message("", msg, channel_id))


                    else:
                        self.call_func(self.event_channel_message, models.Message(name, msg, channel_id))

                if f"!cho@ppy.sh join :#" in line:  # 某人加入房间
                    room = line[line.rfind('#'):]
                    name = line[1:line.find("!")]
                    self.call_func(self.event_someone_joined_room, models.Message(name, room))


class BotApi:
    def __init__(self, bot: OsuBot):
        self.bot = bot

    def send_private_message(self, username, message):
        self.bot.send(f"PRIVMSG {username} :{message}")

    def send_channel_message(self, room_id, message):
        self.bot.send(f"PRIVMSG {room_id} :{message}")

    def room_create(self, room_name, passwd="", free_mods=False, max_member=""):
        self.bot.send(f"PRIVMSG BanchoBot :mp make {room_name}")
        self.bot.waiting_room[room_name] = ""
        while True:
            if self.bot.waiting_room[room_name] != "":
                room_id = self.bot.waiting_room[room_name]
                self.bot.waiting_room.pop(room_name)
                break

        if passwd != "":
            self.bot.send(f"PRIVMSG {room_id} :!mp password {passwd}")
        if free_mods:
            self.bot.send(f"PRIVMSG {room_id} :!mp mods freemod")
        if max_member != "":
            self.bot.send(f"PRIVMSG {room_id} :!mp size {max_member}")

        self.bot.logger(f"Get room id: {room_id}")
        return room_id

    def room_set_passwd(self, room_id, passwd):
        self.bot.send(f"PRIVMSG {room_id} :!mp password {passwd}")

    def room_set_max_member(self, room_id, max_member):
        self.bot.send(f"PRIVMSG {room_id} :!mp size {max_member}")

    def room_set_host(self, room_id, host_name):
        self.bot.send(f"PRIVMSG {room_id} :!mp host {host_name}")

    def room_set_mods(self, room_id, mods):
        self.bot.send(f"PRIVMSG {room_id} :!mp mods {mods}")

    def room_strat_game(self, room_id):
        self.bot.send(f"PRIVMSG {room_id} :!mp start")

    def room_change_map(self, room_id, map_id, mode=""):
        _run = f"PRIVMSG {room_id} :!mp map {map_id}"
        if mode != "":
            _run = f"{_run} {mode}"
        self.bot.send(_run)

