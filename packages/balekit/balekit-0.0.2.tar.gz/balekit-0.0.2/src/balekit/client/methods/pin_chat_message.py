class pinChatMessage:
    def pin_chat_message(self,chat_id,message_id):
        res = self.send_request("pinChatMessage",chat_id=chat_id,message_id=message_id)
        return res