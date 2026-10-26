from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, MetaData

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()




