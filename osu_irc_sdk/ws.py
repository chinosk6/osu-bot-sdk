import socket
import time


class ColorfulPrint:
    class Style:
        DEFAULT = 0
        BOLD = 1
        ITALIC = 3
        UNDERLINE = 4
        ANTIWHITE = 7

    class Color:
        DEFAULT = 39
        BLACK = 30
        RED = 31
        GREEN = 32
        YELLOW = 33
        BLUE = 34
        PURPLE = 35
        CYAN = 36
        WHITE = 37
        LIGHTBLACK_EX = 90
        LIGHTRED_EX = 91
        LIGHTGREEN_EX = 92
        LIGHTYELLOW_EX = 93
        LIGHTBLUE_EX = 94
        LIGHTMAGENTA_EX = 95
        LIGHTCYAN_EX = 96
        LIGHTWHITE_EX = 97

    class BGColor:
        DEFAULT = 49
        BLACK = 40
        RED = 41
        GREEN = 42
        YELLOW = 43
        BLUE = 44
        PURPLE = 45
        CYAN = 46
        WHITE = 47
        LIGHTBLACK_EX = 100
        LIGHTRED_EX = 101
        LIGHTGREEN_EX = 102
        LIGHTYELLOW_EX = 103
        LIGHTBLUE_EX = 104
        LIGHTMAGENTA_EX = 105
        LIGHTCYAN_EX = 106
        LIGHTWHITE_EX = 107

    @staticmethod
    def printout(content, color=Color.DEFAULT, bgcolor=BGColor.DEFAULT, style=Style.DEFAULT):
        print("\033[{};{};{}m{}\033[0m".format(style, color, bgcolor, content))


class OsuIrc:
    def __init__(self, name: str, password: str, host="irc.ppy.sh", port=6667, debug=False):
        self.debug = debug
        self.host = host
        self.port = port
        self.name = name
        self.password = password
        self.wss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.wss.connect((self.host, self.port))
        self.send("PASS " + self.password)
        self.send("NICK " + self.name)
        self.logger("Conncected to Bancho")

    def send(self, text: str):
        self.logger(f"[send] {text}", debug=True)
        self.wss.send((text + '\n').encode())

    def receive(self, size=2048):
        return self.wss.recv(size).decode().lower()

    def logger(self, *args, debug=False, warning=False, error=False, test=False, color=None):
        _tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = ""
        for i in args:
            msg = f"{msg} {i}"
        msg = msg[1:]

        if test:
            ColorfulPrint.printout(f"[{_tm}][TEST] {msg}", ColorfulPrint.Color.LIGHTMAGENTA_EX if color is None else color)
        elif error:
            ColorfulPrint.printout(f"[{_tm}][ERROR] {msg}", ColorfulPrint.Color.RED if color is None else color)
        elif warning:
            ColorfulPrint.printout(f"[{_tm}][WARNING] {msg}", ColorfulPrint.Color.LIGHTYELLOW_EX if color is None else color)
        elif debug and self.debug:
            ColorfulPrint.printout(f"[{_tm}][DEBUG] {msg}", ColorfulPrint.Color.BLUE if color is None else color)
        elif not debug:
            ColorfulPrint.printout(f"[{_tm}][INFO] {msg}", ColorfulPrint.Color.DEFAULT if color is None else color)

    def close(self):
        self.wss.close()

    def __del__(self):
        self.close()
