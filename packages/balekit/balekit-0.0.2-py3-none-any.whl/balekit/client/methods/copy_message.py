class copyMessage:
    def copy_message(self,chat_id,from_chat_id,message_id):
        res = self.send_request("copyMessage",chat_id=chat_id,from_chat_id=from_chat_id,message_id=message_id)
        return res  