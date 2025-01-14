from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, Float, inspect, Index

from aporacle.data.db.sql.models import Base


class Tick(Base):
    __tablename__ = "Tick"
    __table_args__ = (
        Index("os_tick_c_vr_s_p_index", "chain", "voting_round", "symbol", "position"),
    )
    # Change `id` to an auto-incrementing integer primary key
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chain = Column(String(15), nullable=False)
    voting_round = Column(Integer, nullable=False)
    symbol = Column(String(30), nullable=False)
    idx = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    label = Column(String(20), nullable=False)
    feature = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(String(50), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=180)  # 2 minutes
        session.query(Tick).filter(Tick.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
