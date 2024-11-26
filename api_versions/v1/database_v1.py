# Main imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Other imports
from datetime import datetime, UTC

SQLALCHEMY_DATABASE_URL = "sqlite:///wall_of_text.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    text = Column(String, index=True)
    created_at_utc: datetime = Column(DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self):
        return (f"Text(id={self.id}, "
                f"username={self.username}, "
                f"text={self.text}, "
                f"created_at_utc={self.created_at_utc})")


Base.metadata.create_all(bind=engine)
