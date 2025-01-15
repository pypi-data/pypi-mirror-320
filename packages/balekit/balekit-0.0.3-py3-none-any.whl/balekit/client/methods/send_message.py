class sendMessage:
    async def send_message(self,chat_id,text):
        res = await self.send_request("sendMessage",chat_id=chat_id,text=text)
        return res
