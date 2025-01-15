class setChatTitle:
    def set_chat_title(self,chat_id,title):
        res = self.send_request("setChatTitle",chat_id=chat_id,title=title)
        return res