from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, JSON, inspect

from aporacle.data.db.sql.models import Base


class PreparedSymbol(Base):
    __tablename__ = "PreparedSymbol"

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)
    symbol = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    data = Column(JSON, nullable=True)
    data_sizes = Column(Integer, nullable=True)
    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        one_minute = datetime.utcnow() - timedelta(minutes=1)
        session.query(PreparedSymbol).filter(PreparedSymbol.timestamp < one_minute.isoformat()).delete()
        session.commit()
