import pathlib

ROOT_FOLDER = str(pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve())

OPEN_BID: str = "open_bid"
HIGH_BID: str = "high_bid"
LOW_BID: str = "low_bid"
CLOSE_BID: str = "close_bid"
OPEN_ASK: str = "open_ask"
HIGH_ASK: str = "high_ask"
LOW_ASK: str = "low_ask"
CLOSE_ASK: str = "close_ask"

FAST_SMA: str = "fast-sma"
SLOW_SMA: str = "slow-sma"
BODY_RATIO: str = "body-ratio"


PARAMS: str = "params"

EXIT_LONG: str = "exit-long"
EXIT_SHORT: str = "exit-short"
SIGNAL_LONG: str = "long-signal"
SIGNAL_SHORT: str = "short-signal"
ENTRY_LONG: str = "long-entry"
ENTRY_SHORT: str = "short-entry"
