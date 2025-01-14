class exportChatInviteLink:
    def export_chat_invite_link(self,chat_id):
        res = self.send_request("exportChatInviteLink",chat_id=chat_id)
        return res