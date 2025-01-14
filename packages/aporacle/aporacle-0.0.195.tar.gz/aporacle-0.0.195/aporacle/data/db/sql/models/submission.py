from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Float, inspect, Boolean

from aporacle.data.db.sql.models import Base


class Submission(Base):
    __tablename__ = "Submission"

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)
    algorithm_name = Column(String(255), nullable=False)
    submission = Column(Float, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 60 * 24)  # 24 hours
        session.query(Submission).filter(Submission.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
