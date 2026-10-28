from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

class Board(Base):
    __tablename__ = "boards"
    id: Mapped[int] = mapped_column(primary_key=True)
    board_name: Mapped[str] = mapped_column()

class BoardMember(Base):
    __tablename__ = "board_members"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    role: Mapped[str] = mapped_column()