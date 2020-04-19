import socket
import json
import time
import random
from threading import Thread

all_colors = ["black", "red", "blue", "yellow", "green"]

class Client(object):
    socket = None
    address = None
    nickname = "none"
    color = "black"
    new_msg = []
    new_line = []

    def __init__(self, sock, address):
        self.socket = sock
        self.address = address

        self.nickname = self.resv_nick()
        self.send_msg({"msg": ["Server", "Hello, user!"], "lines": []})
        self.color = random.choice(all_colors)

        recv_thread = Thread(target=self.resv_msg)
        recv_thread.start()

    def resv_nick(self):
        try:
            msg = self.socket.recv(1024).decode()
            return msg
        except ConnectionResetError:
            return None

    def resv_msg(self):
        while self.socket is not None:
            try:
                data = self.socket.recv(8000).decode()
                if data:
                    data = json.loads(data)

                    if data["text"] is not None:
                        self.new_msg.append(data["text"])
                    if data["line"] is not None:
                        self.new_line.append(data["line"])

                if len(self.new_msg) > 10:
                    self.close()
                    break
            except ConnectionResetError:
                self.close()
                break
            except ConnectionAbortedError:
                self.close()
                break
            except TimeoutError:
                self.close()
                break

    def send_msg(self, data):
        data = json.dumps(data)
        try:
            self.socket.send(data.encode())
        except ConnectionAbortedError:
            self.close()
        except AttributeError:
            pass

    def get_new_msg(self):
        temp, self.new_msg = self.new_msg, []
        return temp

    def get_new_line(self):
        temp, self.new_line = self.new_line, []
        return temp

    def get_nick(self):
        return self.nickname

    def get_color(self):
        return self.color

    def close(self):
        self.socket.close()
        self.socket = None

    def is_disconnected(self):
        return self.socket is None


class HostServer(object):
    server = None
    user_list = []
    max_clients = 3

    def __init__(self, host="", port=5000, max_clients=10):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))

        print("Слушаю порт", port)
        self.max_clients = max_clients
        self.server.listen(max_clients)

        user_upd_thread = Thread(target=self.upd_users)
        user_upd_thread.start()

    def mainloop(self):
        while True:
            sock, addr = self.server.accept()
            print("\nПодключен пользователь", addr)
            if len(self.user_list) >= self.max_clients:
                sock.close()
                print("Мест нет! Отключен", addr)
            else:
                new_user = Client(sock, addr)
                self.user_list.append(new_user)
            print("Сейчас подключено", len(self.user_list), "пользователей")

    def upd_users(self):
        while True:
            final_data = {"msg": [],
                          "lines": []}
            for user_s in self.user_list:
                if user_s.is_disconnected():
                    print("\nОтключен пользователь '{:}'".format(user_s.get_nick()))
                    self.user_list.remove(user_s)
                    print("Сейчас подключено", len(self.user_list), "пользователей")
                    continue

            for user_s in self.user_list:
                msg_arr = user_s.get_new_msg()
                if not msg_arr:
                    continue
                nick = user_s.get_nick()
                for msg in msg_arr:
                    final_data["msg"].append([nick, msg])

            for user_s in self.user_list:
                line_arr = user_s.get_new_line()
                if not line_arr:
                    continue
                color = user_s.get_color()
                for point1, point2 in line_arr:
                    final_data["lines"].append([point1, point2, color])

            for user_d in self.user_list:
                user_d.send_msg(final_data)
            time.sleep(0.1)


if __name__ == "__main__":
    server = HostServer("", 5000)
    server.mainloop()
    # main()
