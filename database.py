from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# We will replace this string with your actual database credentials soon
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:230607@localhost/behavioral_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()