class sendPhoto:
    def send_photo(self,chat_id,photo,caption="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendPhoto",chat_id=chat_id,photo=photo,caption=caption,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
