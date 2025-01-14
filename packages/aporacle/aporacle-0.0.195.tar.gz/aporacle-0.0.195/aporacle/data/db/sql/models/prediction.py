from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Float, inspect, UniqueConstraint

from aporacle.data.db.sql.models import Base


class Prediction(Base):
    __tablename__ = "Prediction"
    __table_args__ = (UniqueConstraint('chain', 'voting_round', 'feed', 'name', name='uq_prediction'),)

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    prediction = Column(Float, nullable=False)
    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60)
        session.query(Prediction).filter(Prediction.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
