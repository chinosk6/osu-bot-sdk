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

        self.event_channel_message = []
        self.event_private_message = []
        self.event_someone_joined_room = []
        self.event_someone_change_slot = []
        self.event_someone_joined_slot = []
        self.event_room_changed_song = []
        self.event_room_changed_host = []
        self.event_someone_left_room = []
        self.event_match_closed = []

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
                        if "joined in slot" in msg:
                            u_name = msg[:msg.find("joined in slot")].strip()
                            slot = msg[msg.find("joined in slot") + len("joined in slot"):].strip()
                            slot = slot[:-1] if slot.endswith(".") else slot
                            self.call_func(self.event_someone_joined_slot, models.Message(u_name, slot, channel_id))

                        if "moved to slot" in msg:
                            u_name = msg[:msg.find("moved to slot")].strip()
                            slot = msg[msg.find("moved to slot") + len("moved to slot"):].strip()
                            slot = slot[:-1] if slot.endswith(".") else slot
                            self.call_func(self.event_someone_change_slot, models.Message(u_name, slot, channel_id))

                        if "left the game" in msg:
                            u_name = msg[:msg.find("left the game")].strip()
                            self.call_func(self.event_someone_left_room,
                                           models.Message(u_name, f"{u_name} left {channel_id}", channel_id))

                        if "beatmap changed to" in msg:
                            _msg = msg[len("beatmap changed to"):].strip()
                            self.call_func(self.event_room_changed_song, models.Message("", _msg, channel_id))

                        if "became the host" in msg:
                            u_name = msg[:msg.find("became the host")].strip()
                            self.call_func(self.event_room_changed_host, models.Message(u_name, msg, channel_id))

                        if msg == "closed the match":
                            self.call_func(self.event_match_closed, models.Message("", msg, channel_id))


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

    def senf_channel_message(self, room, message):
        self.bot.send(f"PRIVMSG {room} :{message}")

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
