class ResponseFailure(Exception):
    def __init__(self, status_code: str, response: dict):
        self.status_code = status_code
        self.response = response
