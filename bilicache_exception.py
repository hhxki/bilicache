class ErrorCountTooMuch(Exception):
    def __init__(self, info):
        Exception.__init__(self)
        self.info = info

    def __str__(self):
        return self.info


class ErrorChargeVideo(Exception):
    def __init__(self, info):
        Exception.__init__(self)
        self.info = info

    def __str__(self):
        return self.info
