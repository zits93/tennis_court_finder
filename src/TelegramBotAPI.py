import telegram

class TelegramBotAPI:
    def __init__(self):
        self.token = "6330390030:AAE_nYZSO0YhxlHGpd8YFNZUSsXh3m5hLMU"
        self.bot = telegram.Bot(self.token)
        self.chat_id_list = ["6532547898", "6621677164", "6406809129", "1232395613"]
        
    async def send_message(self, text):
        # Test for me
        # await self.bot.send_message(chat_id="6532547898", text=text, parse_mode="Markdown", disable_web_page_preview=True)
        
        # Release to everyone
        for chat_id in self.chat_id_list:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True)
