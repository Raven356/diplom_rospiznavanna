from bot import bot
import io
import uuid

class BotProvider():

    def informUserAboutInsident(self, chat_id, message, photo_bytes):
        bot.send_message(chat_id, message)
        photo = io.BytesIO(photo_bytes)
        photo.name = f'accident{uuid.uuid4()}.jpg'
        bot.send_photo(chat_id, photo)