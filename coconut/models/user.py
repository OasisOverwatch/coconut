from sqlalchemy import Column, Integer, String

from coconut.database import Model


class User(Model):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    blizz_id = Column(String)
    sr = Column(Integer)

    def __init__(self, id, blizz_id, sr):
        self.id = id
        self.blizz_id = blizz_id
        self.sr = sr
