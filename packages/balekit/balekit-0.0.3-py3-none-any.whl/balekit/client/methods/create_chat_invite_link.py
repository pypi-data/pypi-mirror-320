class createChatInviteLink:
    def create_chat_invite_link(self,chat_id):
        res = self.send_request("createChatInviteLink",chat_id=chat_id)
        return res