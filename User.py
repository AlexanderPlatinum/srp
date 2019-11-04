class User(object):
    login: str = ""
    verifier: str = ""
    salt: str = ""

    def __init__(self, login: str, verifier: str, salt: str):
        self.login = login
        self.verifier = verifier
        self.salt = salt

    def to_str(self):
        return self.login + " " + \
               self.verifier + " " \
               + self.salt
