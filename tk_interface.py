from tkinter import *

CLEAR_CMD = {"clear": []}
COLOR_CMD = {"color": ["red"]}
WIDTH_CMD = {"width": [10]}

REQ_DATA = {"commands": [],
            "text": None,
            "line": []}

RES_DATA = {"commands": [],
            "msg_arr": [],
            "lines": []}


class MsgTable(Frame):
    canvas = None
    table = None
    msg_count = 0

    def __init__(self, master=None, **options):
        super().__init__(master, options)
        self.canvas = Canvas(self, width=options['width'])
        if 'width' in options.keys():
            self.canvas.config(width=options['width'])
        if 'height' in options.keys():
            self.canvas.config(height=options['height'])

        msg_scroll = Scrollbar(self, orient='vertical',
                               command=self.canvas.yview)
        msg_scroll.pack(side='right', fill=Y)
        self.canvas.configure(yscrollcommand=msg_scroll.set)

        self.table = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table, anchor='nw')
        self.table.bind('<Configure>', self.conf_scroll)
        self.canvas.pack(side='left')
        self.canvas.bind_all("<MouseWheel>", self.on_scroll)

        self.add_title()

    def conf_scroll(self, agr):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_scroll(self, agr):
        self.canvas.yview_scroll(int(-agr.delta/120), "units")

    def scroll_down(self):
        if self.msg_count > 18:
            self.canvas.yview_scroll(3, "units")

    def add_title(self):
        nick_label = Label(self.table, text="Ник", width=20, relief=RIDGE, bg="#C0C0C0")
        msg_label = Label(self.table, text="Сообщение", width=60, relief=RIDGE, bg="#C0C0C0")

        nick_label.grid(row=self.msg_count, column=0, sticky="W")
        msg_label.grid(row=self.msg_count, column=1, sticky="W", pady=2)
        self.msg_count += 1

    # Split string by \n
    def split_str(self, str):
        new_str = ""
        word_arr = list(str.split())

        str_len = 0
        i = 0
        while i < len(word_arr):
            while str_len < 65 and i < len(word_arr):
                new_str = new_str + " " + word_arr[i]
                str_len += 1 + len(word_arr[i])
                i += 1

            if i != len(word_arr):
                new_str += "\n"
                str_len = 0
        return new_str

    def add_msg(self, nick, msg):
        nick_bg = "#FFFFFF" if nick != "Server" else "#00BFFF"
        nick_label = Label(self.table, text=nick, width=20, relief=RIDGE, bg=nick_bg)

        msg = self.split_str(msg)
        msg_label = Label(self.table, text=msg, anchor=W, justify=LEFT)

        self.pin_msg(nick_label, msg_label)

    def pin_msg(self, label1, label2):
        label1.grid(row=self.msg_count, column=0, sticky="NSW")
        label2.grid(row=self.msg_count, column=1, sticky="W", padx=4)
        self.msg_count += 1
        self.scroll_down()


class DrawField(Canvas):
    first_point = None
    send_func = print

    def __init__(self, master, send_func, **options):
        super().__init__(master, options)
        self.send_func = send_func
        self.bind("<Button-1>", self.mouse_click)
        self.bind("<ButtonRelease-1>", self.mouse_released)

    def draw_line(self, point1, point2, color):
        self.create_line(*point1, *point2, fill=color)

    def draw_new_lines(self, line_arr):
        for point1, point2, color in line_arr:
            self.draw_line(point1, point2, color)

    def mouse_click(self, event):
        print("Clicked at", event.x, event.y)
        self.first_point = (event.x, event.y)

    def mouse_released(self, event):
        print("mouse_released at", event.x, event.y)
        self.send_func(self.first_point, (event.x, event.y))
        self.draw_line(self.first_point, (event.x, event.y), "red")
        self.first_point = None


class ClientGUI(Tk):
    msg_table = None
    msg_entry = None
    send_func = None
    canvas = None

    def __init__(self, send_func):
        super().__init__()
        self.send_func = send_func

        self.msg_table = MsgTable(self, width=500, height=400)
        self.msg_table.grid(row=0, column=0, sticky="NSWE")

        input_frame = Frame()
        input_frame.grid(row=1, column=0, sticky="NSWE")
        self.msg_entry = Entry(input_frame, width=70)
        send_button = Button(input_frame, text="➤", command=self.send_msg,
                             width=10)
        self.msg_entry.grid(row=0, column=0, sticky="NSWE")
        send_button.grid(row=0, column=1, sticky="NSE", padx=10)
        self.bind("<Return>", self.send_msg)

        self.canvas = DrawField(self, self.send_line, width=500, height=400)
        self.canvas.grid(row=0, column=1, sticky="NSWE")

    def config_scroll(self):
        self.msg_canvas.configure(scrollregion=self.msg_canvas.bbox('all'))

    def add_msg(self, nick, msg):
        self.msg_table.add_msg(nick, msg)

    def output_func(self):
        return self.msg_table.add_msg

    def draw_func(self):
        return self.canvas.draw_line

    def set_send_func(self, func):
        self.send_func = func

    def send_msg(self, arg=None):
        msg = str(self.msg_entry.get())
        self.msg_entry.delete(0, 10000)

        data = {"text": msg,
                "line": None}
        self.send_func(data)

    def send_line(self, point1, point2):
        data = {"text": None,
                "line": [point1, point2]}
        self.send_func(data)


if __name__ == "__main__":
    window = ClientGUI()
    f = window.output_func()
    print(f)
    f("Allah", "Edin")
    window.mainloop()
