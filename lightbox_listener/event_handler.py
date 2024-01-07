import requests

from lightbox_listener.models.ListenerData import ListenerData


class CallbackEventHandler:
    def __init__(self):
        pass

    def __request_lightbox(self, x, color):
        requests.get("http://" + x + "/light/" + color)

    def call(self, data: ListenerData):
        self.event_dict[data.reward](self, data=data)

    def _red(self, data: ListenerData):
        color = "red"
        for ip in data.connections:
            self.__request_lightbox(ip, color)

    def _blue(self, data: ListenerData):
        color = "blue"
        for ip in data.connections:
            self.__request_lightbox(ip, color)

    def _green(self, data: ListenerData):
        color = "green"
        for ip in data.connections:
            self.__request_lightbox(ip, color)

    def _meat(self, data: ListenerData):
        print("meat handler")
        print(data)
        pass

    # K: Title of event
    # V: Callable
    event_dict = {
        "red": _red,
        "blue": _blue,
        "green": _green,
        "meat": _meat,
    }
