class leaveChat:
    def leave_chat(self,chat_id):
        res = self.send_request("leaveChat",chat_id=chat_id)
        return res