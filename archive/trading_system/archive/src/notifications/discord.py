import requests


#########################################################################################
#########################################################################################
#########################################################################################


class Discord:
    def __init__(self, message):
        self.WEBHOOK_URL = 'https://discord.com/api/webhooks/1055563087014547486/WxnXCRSiUvQYJNO0Ne-afYU_u_lG3xMBvxrKbTdsvYKspuvVvikGg4eTAkVXMVPPyfdU'
        self.message = message

    def discord_notification(self):
        # Set the data for the HTTP POST request
        data = {'content': self.message}

        # Send the HTTP POST request
        response = requests.post(self.WEBHOOK_URL, json=data)

message = 'Hello, world!'
disc = Discord(message)
disc.discord_notification()