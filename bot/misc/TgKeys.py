from dotenv import load_dotenv
import os

class TgKeys:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("TOKEN")

    def get_token(self):
        return self.token