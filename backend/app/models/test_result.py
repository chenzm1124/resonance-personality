"""测试结果模型"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quiz_record_id: Mapped[int] = mapped_column(ForeignKey("quiz_records.id"), unique=True)
    nine_scores_json: Mapped[str] = mapped_column(Text, comment="9人格得分JSON数组")
    master_personality: Mapped[int] = mapped_column(Integer, comment="主人格索引(0-8)")
    sub_personalities_json: Mapped[str] = mapped_column(Text, comment="2个辅人格索引JSON数组")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关联
    user = relationship("User", back_populates="test_results")
    quiz_record = relationship("QuizRecord", back_populates="test_result")
