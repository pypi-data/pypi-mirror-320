class getChatMembersCount:
    def get_chat_members_count(self,chat_id):
        res = self.send_request("getChatMembersCount",chat_id=chat_id)
        return res