import abc
from enum import Enum

INSTRUMENT_KEY: str = "instrument"
TIME_FRAME_KEY: str = "time-frame"
SIDE_KEY: str = "side"

POS_INSTRUMENT: int = 0
POS_TIME_FRAME: int = 1
POS_SIDE: int = 2

PERIODS_MAP: dict = {
    "monthly": "M1",
    "weekly": "W1",
    "daily": "D1",
    "hourly": "H1",
    "hours": "H",
    "mins": "m",
    "min": "m"
}


class FormatType(Enum):
    DUKASCOPY = "Dukascopy"


FORMAT_STR_TO_ENUM_MAP: dict = {
    "Dukascopy": FormatType.DUKASCOPY
}


class FileNameParser:

    def __init__(self, name_format: FormatType | str):
        if isinstance(name_format, FormatType):
            self._format_type: FormatType = name_format
        else:
            self._format_type: FormatType = FORMAT_STR_TO_ENUM_MAP[name_format]

    def transform(self, file_name: str) -> dict:
        parser_factory: FileNameParserFactory = FileNameParserFactory(self._format_type)
        parser: FormatParser = parser_factory.get_parser()
        return parser.transform(file_name)


class FormatParser(abc.ABC):

    @abc.abstractmethod
    def transform(self, file_name: str) -> dict:
        ...


class DukascopyParser(FormatParser):

    def transform(self, file_name: str) -> dict:
        if len(file_name) == 0:
            raise ValueError("File name cannot be empty")

        name_parts: list = self._split_components(file_name)
        parts: dict = self._parts_to_dict(name_parts)
        parts[TIME_FRAME_KEY] = self._parse_time_frame(parts[TIME_FRAME_KEY])

        return parts

    @staticmethod
    def _split_components(file_name: str) -> list:
        return file_name.split("_")

    @staticmethod
    def _parts_to_dict(parts: list):
        return {INSTRUMENT_KEY: parts[POS_INSTRUMENT],
                TIME_FRAME_KEY: parts[POS_TIME_FRAME],
                SIDE_KEY: parts[POS_SIDE].lower()
                }

    @staticmethod
    def _parse_time_frame(time_frame: str) -> str:
        time_frame_parts: list = time_frame.split(" ")
        if len(time_frame_parts) == 1:
            return PERIODS_MAP[time_frame_parts[0].lower()]
        if len(time_frame_parts) == 2:
            return f"{PERIODS_MAP[time_frame_parts[1].lower()]}{time_frame_parts[0]}"

        raise ValueError(f"Time frame {time_frame}, not recognized for Dukascopy")


class FileNameParserFactory:
    PARSER_MAP: dict = {
        FormatType.DUKASCOPY: DukascopyParser()
    }

    def __init__(self, format_type: FormatType):
        self._format_type: FormatType = format_type

    def get_parser(self) -> FormatParser:
        return self.PARSER_MAP[self._format_type]