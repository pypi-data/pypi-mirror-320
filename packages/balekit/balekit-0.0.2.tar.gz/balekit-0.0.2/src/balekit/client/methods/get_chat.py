class getChat:
    def get_chat(self,chat_id):
        res = self.send_request("getChat",chat_id=chat_id)
        return res