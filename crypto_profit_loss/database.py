from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import engine

Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name


@contextmanager
def scoped():
    s = scoped_session(Session)
    yield s
    s.close()
