import requests


class RapidProClient:

    def __init__(self, thread):
        self.thread = thread

    def send_reply(self, text):
        response = requests.get(url=self.thread.chatbot.request_url, params={
            'from': self.thread.uuid,
            'text': text,
        }, timeout=10)
        return response
