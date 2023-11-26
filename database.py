from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345647Ml#@127.0.0.1:3306/todoapp"

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345647Pl#@localhost/TodoApplicationDatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
