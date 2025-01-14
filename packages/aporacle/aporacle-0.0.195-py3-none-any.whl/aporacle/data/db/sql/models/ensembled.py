from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Float, inspect, Index

from aporacle.data.db.sql.models import Base


class Ensembled(Base):
    __tablename__ = "Ensembled"
    __table_args__ = (Index("os_chain_feed_name_voting_round_index", "chain", "feed", "voting_round"),)

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    estimate = Column(Float, nullable=False)
    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 60 * 24)  # 24 hours
        session.query(Ensembled).filter(Ensembled.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()


class EnsembledEvaluation(Base):
    __tablename__ = "EnsembledEvaluation"
    __table_args__ = (Index("os_chain_feed_vr_name_index", "chain", "feed", "voting_round", "name"),)

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    voting_round = Column(Integer, nullable=False)
    feed = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    # Metrics columns
    r_squared = Column(Float, nullable=True)  # R² (R-squared)
    directional_accuracy = Column(Float, nullable=True)  # Directional Accuracy
    overestimation_frequency = Column(Float, nullable=True)  # Overestimation Frequency
    underestimation_frequency = Column(Float, nullable=True)  # Underestimation Frequency
    average_overestimation_degree = Column(Float, nullable=True)  # Average Overestimation Degree
    average_underestimation_degree = Column(Float, nullable=True)  # Average Underestimation Degree
    mae = Column(Float, nullable=True)  # Mean Absolute Error (MAE)
    rmse_metric = Column(Float, nullable=True)  # Root Mean Squared Error (RMSE)
    mape = Column(Float, nullable=True)  # Mean Absolute Percentage Error (MAPE)
    prediction_stability = Column(Float, nullable=True)  # Prediction Stability (e.g., standard deviation)
    complexity_penalty = Column(Float, nullable=True)  # Complexity Penalty (if applicable)

    timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @staticmethod
    def clear_old_records(session):
        six_hours_ago = datetime.utcnow() - timedelta(seconds=60 * 60 * 24)
        session.query(EnsembledEvaluation).filter(EnsembledEvaluation.timestamp < six_hours_ago.isoformat()).delete()
        session.commit()
