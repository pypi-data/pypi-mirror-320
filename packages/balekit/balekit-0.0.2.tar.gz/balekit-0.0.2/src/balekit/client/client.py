import requests
import json
from .methods import getMe, sendMessage, sendDocument, sendAudio, sendVideo, forwardMessage, copyMessage, banChatMember, unbanChatMember, getChat, leaveChat, promoteChatMember, getChatMembersCount, createChatInviteLink, revokeChatInviteLink, exportChatInviteLink, deleteChatPhoto, setChatTitle, setChatDescription, pinChatMessage, unpinChatMessage, unpinAllChatMessages, editMessageText, deleteMessage, sendPhoto, sendAnimation, sendVoice, sendLocation, sendContact, setChatPhoto, uploadStickerFile

class Bot(getMe, sendMessage, sendDocument, sendAudio, sendVideo, forwardMessage, copyMessage, banChatMember, unbanChatMember, getChat, leaveChat, promoteChatMember, getChatMembersCount, createChatInviteLink, revokeChatInviteLink, exportChatInviteLink, deleteChatPhoto, setChatTitle, setChatDescription, pinChatMessage, unpinChatMessage, unpinAllChatMessages, editMessageText, deleteMessage, sendPhoto, sendAnimation, sendVoice, sendLocation, sendContact, setChatPhoto, uploadStickerFile):
    def __init__(
            self,
            token: str,
            base_url: str = "https://tapi.bale.ai"
            ):
        self.token = token
        self.url = f"{base_url}/bot{str(token)}/"
    
    def send_request(self, method, **kwargs):
        url = self.url + method
        files = None
        
        if method == "sendDocument" and "document" in kwargs:
            files = {"document": kwargs["document"]}
            del kwargs["document"]
        elif method == "sendPhoto" and "photo" in kwargs:
            files = {"photo": kwargs["photo"]}
            del kwargs["photo"]
        elif method == "sendVideo" and "video" in kwargs:
            files = {"video": kwargs["video"]}
            del kwargs["video"]
        elif method == "sendAudio" and "audio" in kwargs:
            files = {"audio": kwargs["audio"]}
            del kwargs["audio"]
        elif method == "sendAnimation" and "animation" in kwargs:
            files = {"animation": kwargs["animation"]}
            del kwargs["animation"]
        elif method == "sendVoice" and "voice" in kwargs:
            files = {"voice": kwargs["voice"]}
            del kwargs["voice"]
        elif method == "setChatPhoto" and "photo" in kwargs:
            files = {"photo": kwargs["photo"]}
            del kwargs["photo"]
        elif method == "uploadStickerFile" and "sticker" in kwargs:
            files = {"sticker": kwargs["sticker"]}
            del kwargs["sticker"]
        req = requests.post(url, files=files, data=kwargs)
        return req.json()
