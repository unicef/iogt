import requests


class RapidProClient:

    def __init__(self, thread):
        self.thread = thread
        if not thread.chatbot.request_url:
            raise Exception('Request URL not defined for Chatbot.')
        self.chatbot_url = thread.chatbot.request_url

    def send_reply(self, text):
        response = requests.get(url=self.chatbot_url, params={
            'from': self.thread.uuid,
            'text': text,
        }, verify=False)
        return response
