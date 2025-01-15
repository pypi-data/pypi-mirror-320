class sendLocation:
    def send_location(self,chat_id,latitude,longitude, horizontal_accuracy=0, reply_to_message_id=0, reply_markup={}):
        res = self.send_request("sendLocation",chat_id=chat_id,latitude=latitude,longitude=longitude,horizontal_accuracy=horizontal_accuracy,reply_to_message_id=reply_to_message_id,reply_markup=reply_markup)
        return res
