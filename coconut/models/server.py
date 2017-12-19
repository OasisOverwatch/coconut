from sqlalchemy import Column, String

from coconut.database import Model


class Server(Model):
    __tablename__ = 'server'
    id = Column(String, primary_key=True)

    def __init__(self, id):
        self.id = id
