class revokeChatInviteLink:
    def revoke_chat_invite_link(self,chat_id):
        res = self.send_request("revokeChatInviteLink",chat_id=chat_id)
        return res