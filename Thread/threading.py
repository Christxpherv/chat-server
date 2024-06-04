import threading


class ChatThread(threading.Thread):
    def __init__(self, sleep_time=0.1, func=None):
        self._stop_event = threading.Event()
        self._sleep_time = sleep_time
        self.func = func

        super().__init__(daemon=True)

    def run(self):
        print(self.isDaemon())
        while not self._stop_event.is_set():
            self.func()
            self._stop_event.wait(self._sleep_time)

    def stop(self, timeout=None):
        self._stop_event.set()