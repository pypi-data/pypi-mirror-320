class sendVoice:
    def send_voice(self,chat_id,voice,caption="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendVoice",chat_id=chat_id,voice=voice,caption=caption,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
