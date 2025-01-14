from datetime import datetime

from sqlalchemy import Column, Integer, inspect, Index, Float, String, UniqueConstraint, DateTime

from aporacle.data.db.sql.models import Base


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
