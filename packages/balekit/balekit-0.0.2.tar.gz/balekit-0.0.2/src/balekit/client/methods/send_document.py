class sendDocument:
    def send_document(self,chat_id,document,caption="", reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendDocument",chat_id=chat_id,document=document,caption=caption,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
