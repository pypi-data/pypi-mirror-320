class banChatMember:
    def ban_chat_member(self,chat_id,user_id):
        res = self.send_request("banChatMember",chat_id=chat_id,user_id=user_id)
        return res