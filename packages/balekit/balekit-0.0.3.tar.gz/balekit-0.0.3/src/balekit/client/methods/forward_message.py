class forwardMessage:
    def forward_message(self,chat_id,from_chat_id,message_id):
        res = self.send_request("forwardMessage",chat_id=chat_id,from_chat_id=from_chat_id,message_id=message_id)
        return res  