import tkinter
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from tkinter.ttk import Style


class GUI:
    def __init__(self, client, debug=False):
        self.client = client
        self.username = None
        self.chat_message = None
        self.debug = debug

        # Create a chat window and then hide it
        self.window = Tk()
        self.username_label_contents = StringVar()
        self.window.bind('<Configure>', self.resize)

        self.chat_window = Canvas(self.window)
        self.chat_window.style = Style()
        self.chat_window.style.theme_use("default")

        self.top_frame = Frame(self.window, height=20)
        self.top_frame.pack(expand=True, fill='x', anchor=N)

        self.username_label = Label(self.top_frame, textvariable=self.username_label_contents)
        self.username_label.pack(expand=True, fill='both', side=tkinter.LEFT)

        self.quit_button = Button(self.top_frame, text="Quit", command=self.quit)
        self.quit_button.pack(padx=10, side=tkinter.LEFT)

        self.chat_line = Label(self.chat_window, width=480, bg="#ABB2B9")
        self.chat_line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.chat_window.pack(fill=BOTH, expand=TRUE, anchor=CENTER)
        self.chat_window.grid_rowconfigure(1, weight=1)
        self.chat_window.grid_columnconfigure(1, weight=1)

        self.chat_contents = Text(self.chat_window,
                                  width=20,
                                  bg="#17202A",
                                  fg="#EAECEE",
                                  padx=5,
                                  pady=5)

        self.chat_contents.pack(expand=True, fill=BOTH, anchor=CENTER, side=BOTTOM)
        self.chat_contents.grid(row=1, column=1, sticky="nsew")
        self.bottom_frame = Frame(self.window)
        self.bottom_frame.pack(expand=True, fill='x', anchor=S, padx=5, pady=5)

        self.message_input = Entry(self.bottom_frame, bg="#2C3E50", fg="#EAECEE")
        self.message_input.pack(expand=True, fill='both', side=tkinter.LEFT)
        self.message_input.bind('<Return>', self.handle_enter)

        self.send_button = Button(master=self.bottom_frame,
                                  text="Send",
                                  height=2,
                                  command=lambda: self.handle_send(self.message_input.get()))

        self.send_button.pack(side=tkinter.LEFT, anchor=CENTER)

        self.request_username()

    def request_username(self):
        self.username = None
        self.window.withdraw()
        self.username = simpledialog.askstring(title="Start Chatting", prompt="Enter a username")

        if self.username is None:
            exit(0)
        else:
            self.username_label_contents.set("Hello " + self.username)

    def start_chatting(self):
        self.layout_chat_window(self.username)
        self.client.start_chatting(username=self.username)
        self.window.mainloop()
        exit(0)

    def layout_chat_window(self, username):
        self.username = username

        # Show the chat window
        self.window.deiconify()
        self.window.title("Chat App")
        self.window.resizable(width=True, height=False)
        self.window.configure(width=620, height=550, bg="#17202A")

        self.chat_contents.config(cursor="arrow")

        # They see me scrollin, they hatin
        scrollbar = Scrollbar(self.chat_window, orient=VERTICAL)
        scrollbar.grid(row=1, column=2, sticky="ns")
        scrollbar.config(command=self.chat_contents.yview)

        self.message_input.focus()
        self.chat_contents.config(state=DISABLED)

    def handle_send(self, chat_message):
        self.debug_print("Sending message - '%s'" % chat_message)
        self.chat_contents.config(state=DISABLED)
        self.chat_message = chat_message
        self.message_input.delete(0, END)

        # Passed on init
        self.chat_contents.config(state=DISABLED)
        self.client.send_message(next_message=chat_message)
        self.message_received("%s (you)> %s" % (self.username, chat_message))

    def message_received(self, message):
        self.debug_print("Received message - '%s'" % message)
        self.chat_contents.config(state=NORMAL)
        self.chat_contents.insert(END, message + "\n\n")
        self.chat_contents.config(state=DISABLED)
        self.chat_contents.see(END)

    def quit(self):
        self.chat_window.destroy()
        self.client.quit()

    def resize(self, event):
        w, h = event.width - 100, event.height - 100
        self.window.config(width=w, height=h)

    def handle_enter(self, ev):
        self.handle_send(self.message_input.get())

    @staticmethod
    def show_error(message, title="Error"):
        messagebox.showerror(title, message)

    def debug_print(self, debug_msg):
        if self.debug:
            print("GUI-DBG: %s" % debug_msg)