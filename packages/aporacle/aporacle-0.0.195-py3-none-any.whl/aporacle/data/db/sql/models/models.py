import uuid
from datetime import datetime
from datetime import timedelta

from sqlalchemy import Column, String, Integer, Float, Index, DateTime
from sqlalchemy import event, func
from sqlalchemy import inspect, JSON, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
metadata = Base.metadata


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


class Metadata(Base):
    __tablename__ = "Metadata"

    key = Column(String(255), primary_key=True, nullable=False)
    value = Column(String(255), nullable=False)
    chain = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"Metadata(key='{self.key}', value='{self.value}', chain='{self.chain}'"


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


class TrainedModel(Base):
    __tablename__ = "TrainedModel"
    __table_args__ = (Index("os_chain_feed_name_target_index", "chain", "feed", "name", "target"),)

    id = Column(String(50), primary_key=True, nullable=False)
    chain = Column(String(25), nullable=False)
    name = Column(String(50), nullable=False)
    feed = Column(String(25), nullable=False)
    symbols = Column(JSON, nullable=False)
    model_type = Column(String(25), nullable=False)

    features = Column(JSON, nullable=False)
    target = Column(Integer, nullable=True)
    scaler_mean = Column(JSON, nullable=True)
    scaler_scale = Column(JSON, nullable=True)
    coefficients = Column(JSON, nullable=True)
    intercept = Column(Float, nullable=True)
    performance = Column(JSON, nullable=True, default={})
    ranking = Column(Integer, nullable=True, default=0)
    last_evaluation_voting_round = Column(Integer, nullable=True, default=0)
    last_evaluation_time = Column(String(55), nullable=True, default='')
    running = Column(Integer, nullable=True, default=0)
    predicting = Column(Integer, nullable=True, default=0)
    r2 = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    running_r_squared = Column(Float, nullable=True, default=0)  # R² (R-squared) - Running evaluation metric
    running_rmse = Column(Float, nullable=True)  # Root Mean Squared Error (RMSE)

    score = Column(Float, nullable=True, default=0)  # Score for how well the model is performing.
    correction_factor = Column(Float, nullable=True)  # Running Correction Factor (if applicable)
    avg_correction_error = Column(Float, nullable=True)  # Average Correction Error
    avg_last_n_corrections = Column(Float, nullable=True)  # Average of Last N Corrections
    timestamp = Column(String(55), nullable=True)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


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
    created_at = Column(Float, default=0, nullable=True)
    ttl = Column(Integer, default=360)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Voter(Base):
    __tablename__ = "Voter"
    # Define a composite index key
    __table_args__ = (
        Index('os_entity_submit_index', "entity_address", "submit_address"),  # Create the index
    )

    id = Column(String(50), primary_key=True, nullable=False)
    chain = Column(String(25), nullable=False)
    # name = Column(String(255), default='', nullable=False)
    entity_address = Column(String(55), nullable=False)
    submit_address = Column(String(55), nullable=False)
    submit_signature_address = Column(String(55), nullable=False)
    signing_policy_address = Column(String(55), nullable=False)
    delegation_address = Column(String(55))
    # sortition_addresses = relationship("SortitionAddress", backref="voter")
    reward_epoch = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    last_update_at_timestamp = Column(String(55), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


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


class EvaluatedModel(Base):
    __tablename__ = "EvaluatedModel"
    __table_args__ = (
        UniqueConstraint('chain', 'model', 'voting_round', name='uq_evaluated_model'),
        Index("et_chain_model_voting_round_index", "chain", "model", "voting_round"),
    )
    # Change `id` to an auto-incrementing integer primary key
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chain = Column(String(15), nullable=False)
    model = Column(String(50), nullable=False)
    feed = Column(String(25), nullable=False)
    voting_round = Column(Integer, nullable=False)
    prediction = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    original_error = Column(Float, nullable=True)
    error_direction_ema = Column(Float, nullable=True)
    error_magnitude = Column(Float, nullable=True)
    error_magnitude_ema = Column(Float, nullable=True)
    direction_consistency = Column(Float, nullable=True)
    correction_factor = Column(Float, nullable=True)
    revised_prediction = Column(Float, nullable=True)
    revised_error = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    evaluation_count = Column(Integer, nullable=False, autoincrement=True)
    status = Column(Integer, nullable=True)
    # Timestamp with default UTC now
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class EvaluatedFeed(Base):
    __tablename__ = "EvaluatedFeed"
    __table_args__ = (
        UniqueConstraint('chain', 'feed', name='uq_evaluated_feed'),
        Index("et_chain_feed_index", "chain", "feed"),
    )
    # Change `id` to an auto-incrementing integer primary key
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chain = Column(String(15), nullable=True)
    feed = Column(String(25), nullable=True)
    correction_factor = Column(Float, nullable=True)  # Correction Factor. Typically, the last observed Moving Average.
    r2_score = Column(Float, nullable=True)
    rmse_score = Column(Float, nullable=True)
    evaluation_voting_round = Column(Integer, nullable=True)
    status = Column(Integer, nullable=True)
    # Timestamp with default UTC now
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

