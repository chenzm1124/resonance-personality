"""答题记录模型"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class QuizRecord(Base):
    __tablename__ = "quiz_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    answers_json: Mapped[str] = mapped_column(Text, default="[]", comment="63题答案JSON数组")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, comment="答题用时(秒)")
    status: Mapped[str] = mapped_column(String(20), default="in_progress", comment="状态: in_progress/completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # 关联
    user = relationship("User", back_populates="quiz_records")
    test_result = relationship("TestResult", back_populates="quiz_record", uselist=False)
