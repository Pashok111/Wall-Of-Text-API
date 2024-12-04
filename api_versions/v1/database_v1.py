# Main imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Other imports
from datetime import datetime, UTC
import tomllib

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
db_file = config["db_file"]
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_file}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, index=True, default=-1)
    username = Column(String, index=True)
    text = Column(String, index=True)
    utc_created_at: datetime = Column(DateTime,
                                      default=lambda: datetime.now(UTC))

    def __repr__(self):
        return (f"Text(id={self.id}, "
                f"username={self.username}, "
                f"text={self.text}, "
                f"created_at_utc={self.utc_created_at})")


Base.metadata.create_all(bind=engine)
