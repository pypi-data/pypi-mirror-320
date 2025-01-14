class deleteChatPhoto:
    def delete_chat_photo(self,chat_id):
        res = self.send_request("deleteChatPhoto",chat_id=chat_id)
        return res