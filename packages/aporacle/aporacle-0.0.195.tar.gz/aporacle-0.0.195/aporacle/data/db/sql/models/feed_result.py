from datetime import datetime, timedelta

from sqlalchemy import Index, Column, Integer, Boolean, Float, inspect, String

from aporacle.data.db.sql.models import Base


class FeedResult(Base):
    __tablename__ = "FeedResult"
    __table_args__ = (Index("os_feed_result_chain_voting_round_feed_index",
                            "chain", "voting_round", "feed"),
                      )

    id = Column(String(255), primary_key=True, nullable=False)  # Changed from Text to String(255)
    chain = Column(String(255), nullable=False)  # Changed from Text to String(255)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)  # Changed from Text to String(255)
    price = Column(Float, nullable=True)
    upper = Column(Float, nullable=True)
    lower = Column(Float, nullable=True)
    rewarded = Column(Boolean, nullable=False, default=False)
    timestamp = Column(String(255), nullable=False)  # Changed from Text to String(255)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 60 * 24)  # 24 hours
        session.query(FeedResult).filter(FeedResult.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
