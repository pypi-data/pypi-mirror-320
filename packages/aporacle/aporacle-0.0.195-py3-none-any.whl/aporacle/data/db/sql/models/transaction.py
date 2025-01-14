from datetime import datetime, timedelta

from komoutils.core.time import the_time_now_is
from sqlalchemy import Index, String, Column, Integer, Boolean, Float, inspect

from aporacle.data.db.sql.models import Base


class Transaction(Base):
    __tablename__ = "Transaction"
    __table_args__ = (Index("os_chain_voting_round_tag_index",
                            "chain", "voting_round", "tag"),
                      )

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    reward_epoch = Column(Integer, nullable=False)
    voting_round = Column(Integer, nullable=False)
    tag = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    payload = Column(String(1024), nullable=False)
    valid = Column(Boolean, nullable=False, default=True)
    timestamp = Column(String(255), nullable=False)
    created_at = Column(Float, default=the_time_now_is())
    ttl = Column(Integer, default=360)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 5)  # 5 minutes
        session.query(Transaction).filter(Transaction.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
