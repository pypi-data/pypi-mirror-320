from bson import ObjectId
from dataclasses import dataclass
from datetime import datetime
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_serializer,
    model_serializer,
    model_validator,
)
from pymongo import ASCENDING, DESCENDING
from typing import Optional, Union

from fmp.consts import Currency


class ListBaseModel(RootModel):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return len(self.root)


class MongoModel(BaseModel):
    """Base MongoDB model class."""

    # mongo_object_id: Optional[PydanticObjectId] = None
    mongo_object_id: Optional[ObjectId]

    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)


@dataclass
class MongoDBIndex:
    key: str
    direction: Union[ASCENDING, DESCENDING]

    @property
    def as_tuple(self) -> tuple[str, Union[ASCENDING, DESCENDING]]:
        return self.key, self.direction


@dataclass
class ForexPair:
    base: Currency
    quote: Currency

    @property
    def yf(self) -> str:
        return f"{self.base.value}{self.quote.value}=X"

    @property
    def raw(self) -> str:
        return f"{self.base.value}{self.quote.value}"

    @classmethod
    def from_raw(cls, raw_str: str) -> "ForexPair":
        if len(raw_str) != 6:
            raise ValueError(f"Invalid Forex pair format: {raw_str}")
        return cls(base=Currency(raw_str[:3]), quote=Currency(raw_str[3:]))

    @model_serializer
    def serializer(self) -> str:
        return self.raw

    @property
    def currencies(self) -> tuple[Currency, Currency]:
        return self.base, self.quote

    @classmethod
    def parse_list(cls, list_raw_str: list[str]) -> list["ForexPair"]:
        return [cls.from_raw(raw_str) for raw_str in list_raw_str]


class ForexTicker(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ticker: ForexPair = Field(alias="Ticker")
    timestamp_datetime: Optional[AwareDatetime] = Field(alias="Datetime", default=None)
    timestamp_date: Optional[datetime] = Field(alias="Date", default=None)
    close: float = Field(alias="Close")
    high: float = Field(alias="High")
    low: float = Field(alias="Low")
    open: float = Field(alias="Open")

    @field_serializer("ticker")
    def ticker_serializer(self, ticker: ForexPair) -> str:
        return ticker.raw

    @model_validator(mode="after")
    def date_or_datetime(self) -> "ForexTicker":
        if not (self.timestamp_datetime or self.timestamp_date):
            raise ValueError("Either timestamp_datetime or timestamp_date must be provided.")
        return self

    @model_validator(mode="before")
    def str_to_ticker(self) -> "ForexTicker":
        if isinstance(self.get("ticker"), str):
            self["ticker"] = ForexPair.from_raw(self["ticker"])
        return self


class ForexTickerList(ListBaseModel):
    root: list[ForexTicker]
