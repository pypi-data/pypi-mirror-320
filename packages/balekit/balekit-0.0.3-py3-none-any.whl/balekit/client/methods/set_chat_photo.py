class setChatPhoto:
    def set_chat_photo(self,chat_id,photo):
        res = self.send_request("setChatPhoto",chat_id=chat_id,photo=photo)
        return res  