from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from coconut.config import get_config

Base = declarative_base()
Session = sessionmaker()


class DBManager(object):
    def __init__(self, uri):
        self.engine = create_engine(uri)
        Session.configure(bind=self.engine)
        self.session = Session()


config = get_config()
db = DBManager(config.SQLALCHEMY_DATABASE_URI)


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete)
    operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        # Prevent changing ID of object
        kwargs.pop('id', None)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, Base):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True