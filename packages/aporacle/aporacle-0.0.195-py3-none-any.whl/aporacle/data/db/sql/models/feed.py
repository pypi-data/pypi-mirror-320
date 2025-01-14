from sqlalchemy import Column, Integer, inspect, Index, Float, String, event, func
from sqlalchemy.orm import Session

from aporacle.data.db.sql.models import Base


class Feed(Base):
    __tablename__ = "Feed"
    __table_args__ = (
        Index("os_feed_base_quote_index", "name", "base", "quote"),
    )

    id = Column(String(35), primary_key=True, nullable=False)
    name = Column(String(30), nullable=False)
    code = Column(Integer, nullable=False, unique=True)  # Ensure `unique=True` for uniqueness
    base = Column(String(15), nullable=True)  # New attribute: Base currency
    quote = Column(String(10), nullable=True)  # New attribute: Quote currency
    address = Column(String(255), nullable=True)  # New attribute: Feed address
    category = Column(String(10), nullable=True)  # New attribute: Feed category
    decimals = Column(Integer, nullable=True)  # New attribute: Decimal places
    status = Column(Integer, nullable=False)  # Status of the feed
    start_collecting_data_at_timestamp = Column(Float, default=0, nullable=True)  # Start collecting data timestamp
    end_collecting_data_at_timestamp = Column(Float, default=0, nullable=True)  # End collecting data timestamp
    begin_support_at_timestamp = Column(Float, default=0, nullable=True)  # Begin support timestamp
    end_support_at_timestamp = Column(Float, default=0, nullable=True)  # End support timestamp
    last_update_at_timestamp = Column(String(255), nullable=False)  # Timestamp for last update

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


@event.listens_for(Feed, "before_insert")
def generate_code(mapper, connection, target):
    """
    Generate a sequential code for a Feed instance before inserting it into the database.
    Codes are generated as 100000, 110000, 120000, ...
    """
    session = Session(bind=connection)
    # Retrieve the maximum existing code from the Feed table
    max_code = session.query(func.max(Feed.code)).scalar()

    # Determine the new code based on the max code
    if max_code is None:
        new_code = 1000000  # Start from 1000000 if no existing feeds
    else:
        new_code = max_code + 100000  # Increment by 100000 for each new feed

    target.code = new_code
    session.close()
