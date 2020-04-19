import socket
import json
import time
from tk_interface import ClientGUI
from threading import Thread


def print_console(msg):
    print(msg)


class ServerInterface(object):
    socket = None
    output_func = None
    draw_func = print

    def __init__(self, nick, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.send(nick.encode())
        print("Подключение с {:} установлено!".format(HOST))
        print("(пустой ввод - оборвать подключение)")
        print("=" * 40)

        recv_thread = Thread(target=self.resv_msg)
        recv_thread.start()

    def send_msg(self, msg):
        if self.socket is None:
            return
        data = json.dumps(msg)
        self.socket.send(data.encode())

    def send_func(self):
        return self.send_msg

    def set_output_func(self, func):
        self.output_func = func

    def set_draw_func(self, func):
        self.draw_func = func

    def resv_msg(self):
        while self.socket is not None:
            try:
                data = self.socket.recv(8000).decode()
                if data:
                    data = json.loads(data)
                    # if data["msg"] is not []:
                    for nick, msg in data["msg"]:
                        self.output_func(nick, msg)

                    # if data["lines"] is not []:
                    for p1, p2, color in data["lines"]:
                        self.draw_func(p1, p2, color)

            except ConnectionResetError:
                self.close()
                break
            except ConnectionAbortedError:
                self.close()
                break
            except:
                # TODO: find error
                print("Unknown error!", len(data), data)
                continue

    def close(self):
        print("Close the connection")
        self.socket.close()
        self.socket = None
        self.output_func("Server", "Server was turned off")


if __name__ == "__main__":
    # TODO: def main()
    HOST = "fairayhome.ddns.net"
    PORT = 420
    nickname = input("Введите своё имя: ")

    window = ClientGUI(print_console)
    server = ServerInterface(nickname, HOST, PORT)

    server.set_output_func(window.output_func())
    server.set_draw_func(window.draw_func())
    window.set_send_func(server.send_func())

    window.mainloop()
    # main()
