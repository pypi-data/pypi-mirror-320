class sendMessage:
    def send_message(self,chat_id,text):
        res = self.send_request("sendMessage",chat_id=chat_id,text=text)
        return res
