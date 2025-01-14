class unpinAllChatMessages:
    def unpin_all_chat_messages(self,chat_id):
        res = self.send_request("unpinAllChatMessages",chat_id=chat_id)
        return res