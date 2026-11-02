
from sqlalchemy import (
    Boolean,
    ForeignKey,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    is_personal: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # users: Mapped[list["BoardUser"]] = relationship(
    #     back_populates="board",
    #     cascade="all, delete-orphan"
    # )
    #
    # tasks: Mapped[list["Task"]] = relationship(
    #     back_populates="board",
    #     cascade="all, delete-orphan"
    # )


class BoardUser(Base):
    __tablename__ = "board_users"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    board_id: Mapped[int] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="member",
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            "user_id",
            "board_id",
            name="pk_board_users"
        ),
    )

    # user: Mapped["User"] = relationship(
    #     back_populates="boards"
    # )
    #
    # board: Mapped["Board"] = relationship(
    #     back_populates="users"
    # )
