from komoutils.core.time import the_time_in_iso_now_is
from sqlalchemy import Index, Column, Integer, String, Float, JSON, inspect

from aporacle.data.db.sql.models import Base


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
