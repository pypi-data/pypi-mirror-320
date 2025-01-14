import random
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, inspect, event, Index, func
from sqlalchemy.orm import Session

from aporacle.data.db.sql.models import Base
from aporacle.data.db.sql.models.models import Feed

class Symbol(Base):
    __tablename__ = "Symbol"
    __table_args__ = (
        Index("os_symbol_feed_name_index", "feed", "name"),
    )
    id = Column(String(50), primary_key=True, nullable=False)
    name = Column(String(50), nullable=False)
    code = Column(Integer, nullable=False, unique=True)  # Ensure `unique=True` for uniqueness
    feed = Column(String(50), nullable=False)
    status = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


@event.listens_for(Symbol, "before_insert")
def generate_symbol_code(mapper, connection, target):
    """
    Generate a sequential symbol code that includes the Feed code as a prefix.
    If a specified feed does not exist, create the feed automatically.

    E.g., if a Feed has code `100000`, the first symbol under this feed will be `100010`,
    the second will be `100020`, and so on.
    """
    session = Session(bind=connection)

    # Retrieve the feed's code based on the feed name
    feed = session.query(Feed).filter_by(name=target.feed).first()

    # If the feed does not exist, create a new one
    if feed is None:
        # Create a new feed with a generated ID and the provided feed name
        feed = Feed(
            id=str(uuid.uuid4()),
            name=target.feed,
            status=1,
            timestamp=datetime.utcnow().isoformat()
        )
        session.add(feed)
        session.flush()  # Flush to ensure `before_insert` triggers and `code` is generated

    # The feed's code is now available
    feed_code = feed.code

    # Find the highest existing code for the symbols under the specified feed
    max_symbol_code = session.query(func.max(Symbol.code)).filter(Symbol.feed == target.feed).scalar()

    # Determine the new symbol code
    if max_symbol_code is None:
        new_symbol_code = feed_code + 1  # Start from feed_code + 10 for the first symbol
    else:
        new_symbol_code = max_symbol_code + 1  # Increment by 10 for each new symbol

    target.code = new_symbol_code
    session.close()