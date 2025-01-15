class unbanChatMember:
    def unban_chat_member(self,chat_id,user_id,only_if_banned=True):
        res = self.send_request("banChatMember",chat_id=chat_id,user_id=user_id,only_if_banned=only_if_banned)
        return res