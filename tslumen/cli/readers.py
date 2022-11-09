"""Dataframe readers (mostly wrappers around Pandas ``read_`` functions)."""
from typing import Optional, Any, List
from dataclasses import dataclass
from abc import ABC

import pandas as pd
from omegaconf import MISSING

__all__ = ["Reader", "ReaderCsv", "ReaderFwf", "ReaderExcel"]


@dataclass
class Reader(ABC):
    """Base class for all readers."""

    path: str = MISSING

    def __init__(self, **kwargs: Any) -> None:
        self.path = kwargs.pop("path")
        self.kwargs = kwargs


@dataclass(init=False)
class ReaderCsv(Reader):
    """CSV file reader."""

    _target_: str = "tslumen.cli.readers.ReaderCsv"

    sep: str = ","
    delimiter: Optional[str] = None
    header: Any = "infer"
    index_col: int = 0
    prefix: Optional[str] = None
    skipinitialspace: bool = False
    skiprows: Optional[int] = None
    skipfooter: int = 0
    nrows: Optional[int] = None
    skip_blank_lines: bool = True
    compression: str = "infer"
    thousands: Optional[str] = None
    decimal: str = "."
    lineterminator: Optional[str] = None
    quotechar: str = "'"
    quoting: int = 0
    doublequote: bool = True
    escapechar: Optional[str] = None
    comment: Optional[str] = None
    encoding: Optional[str] = None
    delim_whitespace: bool = False

    def read(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, **self.kwargs)
        df.index = pd.to_datetime(df.index)
        return df


@dataclass(init=False)
class ReaderFwf(Reader):
    """Fixed-width formatted file reader."""

    _target_: str = "tslumen.cli.readers.ReaderFwf"

    sep: str = ","
    colspecs: Any = "infer"
    widths: Any = None
    infer_nrows: int = 100

    def read(self) -> pd.DataFrame:
        df = pd.read_fwf(self.path, **self.kwargs)
        df.set_index(df.columns[0])
        df.index = pd.to_datetime(df.index)
        return df


@dataclass(init=False)
class ReaderExcel(Reader):
    """Excel file reader."""

    _target_: str = "tslumen.cli.readers.ReaderExcel"

    sheet_name: Any = 0
    header: Any = 0
    names: Optional[List[str]] = None
    index_col: int = 0
    skiprows: Optional[int] = None
    nrows: Optional[int] = None
    thousands: Optional[str] = None
    comment: Optional[str] = None
    skipfooter: int = 0

    def read(self) -> pd.DataFrame:
        df = pd.read_excel(self.path, **self.kwargs)
        df.index = pd.to_datetime(df.index)
        return df
