class sendVideo:
    def send_video(self,chat_id,video,caption="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendVideo",chat_id=chat_id,video=video,caption=caption,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
