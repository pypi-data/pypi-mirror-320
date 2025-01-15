class deleteMessage:
    def delete_message(self, chat_id, message_id):
        res = self.send_request("deleteMessage",chat_id=chat_id,message_id=message_id)
        return res