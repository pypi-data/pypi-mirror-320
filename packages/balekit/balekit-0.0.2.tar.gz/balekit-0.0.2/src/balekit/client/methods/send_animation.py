class sendAnimation:
    def send_animation(self,chat_id,animation,caption="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendAnimation",chat_id=chat_id,animation=animation,caption=caption,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
