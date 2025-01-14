from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .symbol import Symbol
from .tick import Tick
# Import all model classes
from .metadata import Metadata
from .prediction import Prediction
from .prepared_symbol import PreparedSymbol
from .ensembled import Ensembled
from .provider import Provider
from .evaluation import Evaluation
from .transaction import Transaction
from .voter import Voter
from .feed import Feed
from .trained_model import TrainedModel
from .feed_result import FeedResult
from .evaluated_model import EvaluatedModel
from .evaluated_feed import EvaluatedFeed

# Expose all model classes
__all__ = [
    'Base',
    'Metadata',
    'Prediction',
    'PreparedSymbol',
    'Ensembled',
    'Provider',
    'Evaluation',
    'Transaction',
    'Voter',
    'Feed',
    'TrainedModel',
    'FeedResult',
    'Symbol',
    'Tick',
    'EvaluatedModel',
    'EvaluatedFeed'
]


def get_declarative_base():
    return Base
