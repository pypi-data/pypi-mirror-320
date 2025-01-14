from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Float, inspect, Index, UniqueConstraint

from aporacle.data.db.sql.models import Base


class Evaluation(Base):
    __tablename__ = "Evaluation"
    __table_args__ = (
        UniqueConstraint('chain', 'voting_round', 'feed', 'name', name='uq_evaluation'),
        Index("os_chain_feed_name_index", "chain", "feed", "name")
    )

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    prediction = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    correction_factor = Column(Float, nullable=True)
    avg_correction_error = Column(Float, nullable=True)  # Average Correction Error
    avg_last_n_corrections = Column(Float, nullable=True)  # Average of Last N Corrections
    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 60 * 24)  # 24 hours
        session.query(Evaluation).filter(Evaluation.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
