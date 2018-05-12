from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///rich.db')
Base = declarative_base()

from .user import *
from .trades import *

Base.metadata.create_all(engine)
