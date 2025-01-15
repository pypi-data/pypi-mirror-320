class sendContact:
    def send_contact(self,chat_id,phone_number,first_name, lastname="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendLocation",chat_id=chat_id,phone_number=phone_number,first_name=first_name,lastname=lastname,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
