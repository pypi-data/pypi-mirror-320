class sendAudio:
    def send_audio(self,chat_id,audio,caption="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendAudio",chat_id=chat_id,audio=audio,caption=caption,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
