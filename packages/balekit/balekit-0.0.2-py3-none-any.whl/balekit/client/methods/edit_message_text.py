class editMessageText:
    def edit_message_text(self, chat_id=None, message_id=None, text="", reply_markup=None):
        res = self.send_request("editMessageText",chat_id=chat_id,message_id=message_id,text=text,reply_markup=reply_markup)
        return res