from dataclasses import dataclass, field

from komoutils.core.time import the_time_in_iso_now_is


@dataclass
class VotingRoundBase:
    chain: str
    reward_epoch: int
    voting_round: int
    voting_round_start: int
    voting_round_end: int
    block_number: int = 0
    collection_range: list = field(default_factory=list)
    timestamp: str = the_time_in_iso_now_is()


@dataclass
class SubscribeRequest:
    type: str = ""
    topics: list = field(default_factory=list)
    heartbeat: bool = True
