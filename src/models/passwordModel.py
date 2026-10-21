class Password:

    def __init__(self, hash):
        self._hash = hash
        self._password = hash

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new):
        self._password = new