from sqlalchemy import Column, Integer, inspect, Index, Float, String

from aporacle.data.db.sql.models import Base


class Voter(Base):
    __tablename__ = "Voter"
    # Define a composite index key
    __table_args__ = (
        Index('os_entity_submit_index', "entity_address", "submit_address"),  # Create the index
    )

    id = Column(String(255), primary_key=True, nullable=False)
    chain = Column(String(255), nullable=False)
    # name = Column(String(255), default='', nullable=False)
    entity_address = Column(String(255), nullable=False)
    submit_address = Column(String(255), nullable=False)
    submit_signature_address = Column(String(255), nullable=False)
    signing_policy_address = Column(String(255), nullable=False)
    delegation_address = Column(String(255), nullable=False)
    # sortition_addresses = relationship("SortitionAddress", backref="voter")
    reward_epoch = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    last_update_at_timestamp = Column(String(255), nullable=False)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}