from switchai import SwitchAI


class SlideMaker:
    def __init__(self, chat_client: SwitchAI, image_generation_client: SwitchAI):
        self.chat_client = chat_client
        self.image_generation_client = image_generation_client

    def generate_slides(self, description: str, slide_count: int):
        pass
