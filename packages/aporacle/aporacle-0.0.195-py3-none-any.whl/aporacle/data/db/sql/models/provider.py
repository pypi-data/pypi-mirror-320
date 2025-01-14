from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Float, inspect, JSON

from aporacle.data.db.sql.models import Base


class Provider(Base):
    __tablename__ = "Provider"

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    reward_epoch = Column(Integer, nullable=True)
    reward_epoch_start = Column(Float, nullable=True)
    reward_epoch_end = Column(Float, nullable=True)
    voting_round = Column(Integer, nullable=False)
    voting_round_start = Column(Float, nullable=False)
    voting_round_end = Column(Float, nullable=False)
    voting_round_submission_start_buffer = Column(Integer, nullable=False, default=20)
    voting_round_submission_end_buffer = Column(Integer, nullable=False, default=10)
    feeds = Column(JSON, nullable=False)
    voters = Column(JSON, nullable=False)
    commits = Column(JSON, nullable=True)
    reveals = Column(JSON, nullable=True)
    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 5)
        session.query(Provider).filter(Provider.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
