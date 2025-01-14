class uploadStickerFile:
    def upload_sticker_file(self,user_id,sticker):
        res = self.send_request("uploadStickerFile",user_id=user_id,sticker=sticker)
        return res