import traceback

SUPPORTED_SERVICES = []
try:
    from linebot import LineBotApi
    from linebot.exceptions import LineBotApiError
    from linebot.models import TextSendMessage
    SUPPORTED_SERVICES.append('line')
    print('Line library loaded.')
except:
    print('Line library is not found.')

try:
    import telegram
    SUPPORTED_SERVICES.append('telegram')
    print('Tenegram library loaded.')
except:
    print('Telegram library is not found.')

class API:
    """Abstract API class.
    """

    def __init__(self):
        pass

    def send_message(self, text: str, receiver: str):
        raise NotImplementedError

    def broadcast_message(self, text: str):
        raise NotImplementedError

class LineAPI(API):
    """Line API.

    Parameters
    ----------
    client_list : list
        Client list including pairs of name and token. Token can be found at https://developers.line.biz/console/. 
    channel_access_token : str
        Channel_access_token. Can be found at https://developers.line.biz/console/.
    """

    def __init__(self, client_list: list, channel_access_token: str):
        self.line_api = LineBotApi(channel_access_token)
        self.client_list = client_list

    def send_message(self, text: str, receiver: str):
        try:
            self.line_api.push_message(self.client_list[receiver], TextSendMessage(text=text))
            return True
        except LineBotApiError as e:
            print(e.error.message)
            print(e.error.details)
        except:
            traceback.print_exc()
        return False
    
    def broadcast_message(self, text: str):
        try:
            self.line_api.broadcast(TextSendMessage(text=text))
            return True
        except LineBotApiError as e:
            print(e.error.message)
            print(e.error.details)
        except:
            traceback.print_exc()
        return False

class TelegramAPI(API):
    """Telegram API.

    Parameters
    ----------
    client_list : list
        Client list including pairs of name and user id.
    bot_token : str
        bot_token. Can be found at @BotFather.
    """

    def __init__(self, client_list, bot_token):
        self.telegram_api = telegram.Bot(token=bot_token)
        self.client_list = client_list

        self.chat_ids = self._update_chat_ids() 

    def _update_chat_ids(self):
        chat_ids = {}
        for update in self.telegram_api.get_updates():
            username = update.message.chat.username
            chat_id = update.message.chat_id
            chat_ids[username] = chat_id
        return chat_ids

    def _get_chat_id(self, client):
        try:
            chat_id = int(client)
        except:
            chat_id = self.chat_ids[client]
        return chat_id

    def send_message(self, text: str, receiver: str):
        try:
            chat_id = self._get_chat_id(self.client_list[receiver])
            self.telegram_api.send_message(chat_id=chat_id, text=text)
            return True
        except:
            traceback.print_exc()
            return False
    
    def broadcast_message(self, text: str):
        return False

class DiscordAPI(API):
    def __init__(self):
        pass

    def send_message(self, text: str, receiver: str):
        return False

    def broadcast_message(self, text: str):
        return False
