class setChatDescription:
    def set_chat_description(self,chat_id,description):
        res = self.send_request("setChatDescription",chat_id=chat_id,description=description)
        return res