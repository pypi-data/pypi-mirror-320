#!/usr/bin/env python3
#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
# Copyright (c) 2023-2025 Yunqi Inc. All rights reserved.
#

import array
import datetime
import decimal
import functools
import logging
import platform
import random
import re
import string
from enum import Enum
from json import JSONEncoder
from random import choice
from typing import Any, Callable, Dict, Iterator, List, Literal, Optional, Tuple, Type

import clickzetta.zettapark
from clickzetta.zettapark._connector import (
    CONNECTOR_VERSION as connector_version,
    ClickzettaCursor,
    ResultMetadata,
    pandas,
)
from clickzetta.zettapark._internal.error_message import (
    ZettaparkClientExceptionMessages,
)
from clickzetta.zettapark._internal.reserved_words import RESERVED_WORDS
from clickzetta.zettapark._internal.type_utils import ResultRowConverter
from clickzetta.zettapark.row import Row

VOLUME_PREFIX = ""


# https://doc.clickzetta.com/
UNQUOTED_ID_PATTERN = r"([a-zA-Z_][\w\$]{0,255})"
QUOTED_ID_PATTERN = '(("|`)([^"]|""|){1,255}("|`))'
ID_PATTERN = f"({UNQUOTED_ID_PATTERN}|{QUOTED_ID_PATTERN})"

# Valid name can be:
#   identifier
#   identifier.identifier
#   identifier.identifier.identifier
#   identifier..identifier
#   `identifier`.`identifier`.`identifier`
OBJECT_RE_PATTERN = re.compile(
    f"^(({ID_PATTERN}\\.){{0,2}}|({ID_PATTERN}\\.\\.)){ID_PATTERN}$"
)


# "%?" is for table volume
VOLUME_NAME_PATTERN = f"(%?{ID_PATTERN})"

# Prefix for allowed temp object names
TEMP_OBJECT_NAME_PREFIX = "zettapark_temp_"
ALPHANUMERIC = string.digits + string.ascii_lowercase

SELECT_SQL_PREFIX_PATTERN = re.compile(
    r"^(\s*/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)?((\s)*--.*?\n)*(\s|\()*(select|with)",
    re.IGNORECASE,
)


GENERATED_PY_FILE_EXT = (".pyc", ".pyo", ".pyd", ".pyi")

INFER_SCHEMA_FORMAT_TYPES = ("PARQUET", "ORC", "AVRO", "JSON", "CSV")

COPY_OPTIONS = {
    "ON_ERROR",
    "SIZE_LIMIT",
    "PURGE",
    "RETURN_FAILED_ONLY",
    "MATCH_BY_COLUMN_NAME",
    "ENFORCE_LENGTH",
    "TRUNCATECOLUMNS",
    "FORCE",
    "LOAD_UNCERTAIN_FILES",
}

NON_FORMAT_TYPE_OPTIONS = {
    "PATTERN",
    "VALIDATION_MODE",
    "FILE_FORMAT",
    "FORMAT_NAME",
    "FILES",
    # The following are not copy into SQL command options but client side options.
    "INFER_SCHEMA",
    "FORMAT_TYPE_OPTIONS",
    "TARGET_COLUMNS",
    "TRANSFORMATIONS",
    "COPY_OPTIONS",
}

TEMPORARY_STRING = ""
SCOPED_TEMPORARY_STRING = ""
SUPPORTED_TABLE_TYPES = ["temp", "temporary", "transient"]


class TempObjectType(Enum):
    TABLE = "TABLE"
    VIEW = "VIEW"
    VOLUME = "VOLUME"
    FUNCTION = "FUNCTION"
    FILE_FORMAT = "FILE_FORMAT"
    COLUMN = "COLUMN"
    TABLE_FUNCTION = "TABLE_FUNCTION"
    DYNAMIC_TABLE = "DYNAMIC_TABLE"
    AGGREGATE_FUNCTION = "AGGREGATE_FUNCTION"
    CTE = "CTE"


def validate_object_name(name: str):
    if not OBJECT_RE_PATTERN.match(name):
        raise ZettaparkClientExceptionMessages.GENERAL_INVALID_OBJECT_NAME(name)


def get_version() -> str:
    return clickzetta.zettapark.__version__


def get_python_version() -> str:
    return platform.python_version()


def get_connector_version() -> str:
    return ".".join([str(d) for d in connector_version if d is not None])


def get_os_name() -> str:
    return platform.system()


def get_application_name() -> str:
    return "PythonZettapark"


def is_single_quoted(name: str) -> bool:
    return name.startswith("'") and name.endswith("'")


def unwrap_single_quote(name: str) -> str:
    new_name = name.strip()
    if is_single_quoted(new_name):
        new_name = new_name[1:-1]
    new_name = new_name.replace("\\'", "'")
    return new_name


def is_sql_select_statement(sql: str) -> bool:
    return SELECT_SQL_PREFIX_PATTERN.match(sql) is not None


_SHOW_SQL_PREFIX_PATTERN = re.compile(
    r"^(\s*/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)?((\s)*--.*?\n)*(\s|\()*(show)",
    re.IGNORECASE,
)


def is_sql_show_statement(sql: str) -> bool:
    return _SHOW_SQL_PREFIX_PATTERN.match(sql) is not None


def random_number() -> int:
    """Get a random unsigned integer."""
    return random.randint(0, 2**31)


def parse_positional_args_to_list(*inputs: Any) -> List:
    """Convert the positional arguments to a list."""
    if len(inputs) == 1:
        return (
            [*inputs[0]] if isinstance(inputs[0], (list, tuple, set)) else [inputs[0]]
        )
    else:
        return [*inputs]


def str_to_enum(value: str, enum_class: Type[Enum], except_str: str) -> Enum:
    try:
        return enum_class(value)
    except ValueError:
        raise ValueError(
            f"{except_str} must be one of {', '.join([e.value for e in enum_class])}"
        )


def random_name_for_temp_object(object_type: TempObjectType) -> str:
    return f"{TEMP_OBJECT_NAME_PREFIX}{object_type.value.lower()}_{generate_random_alphanumeric().lower()}"


def generate_random_alphanumeric(length: int = 10) -> str:
    return "".join(choice(ALPHANUMERIC) for _ in range(length))


def column_to_bool(col_):
    """A replacement to bool(col_) to check if ``col_`` is None or Empty.

    ``Column.__bool__` raises an exception to remind users to use &, |, ~ instead of and, or, not for logical operations.
    The side-effect is the implicit call like ``if col_`` also raises an exception.
    Our internal code sometimes needs to check an input column is None, "", or []. So this method will help it by writeint ``if column_to_bool(col_): ...``
    """
    if isinstance(col_, clickzetta.zettapark.Column):
        return True
    return bool(col_)


def result_set_to_rows(
    result_set: List[Any],
    result_meta: Optional[List[ResultMetadata]] = None,
    case_sensitive: bool = False,
) -> List[Row]:
    col_names = [col.name for col in result_meta] if result_meta else None
    rows = []
    row_struct = Row
    if col_names:
        row_struct = (
            Row._builder.build(*col_names).set_case_sensitive(case_sensitive).to_row()
        )
    row_converter = ResultRowConverter(result_meta)
    for data in result_set:
        if data is None:
            raise ValueError("Result returned from Python connector is None")
        row = row_struct(*row_converter(data))
        rows.append(row)
    return rows


def result_set_to_iter(
    result_set: ClickzettaCursor,
    result_meta: Optional[List[ResultMetadata]] = None,
    case_sensitive: bool = False,
) -> Iterator[Row]:
    col_names = [col.name for col in result_meta] if result_meta else None
    row_struct = Row
    if col_names:
        row_struct = (
            Row._builder.build(*col_names).set_case_sensitive(case_sensitive).to_row()
        )
    for data in result_set:
        if data is None:
            raise ValueError("Result returned from Python connector is None")
        row = row_struct(*data)
        yield row


class PythonObjJSONEncoder(JSONEncoder):
    """Converts common Python objects to json serializable objects."""

    def default(self, value):
        if isinstance(value, (bytes, bytearray)):
            return value.hex()
        elif isinstance(value, decimal.Decimal):
            return float(value)
        elif isinstance(value, (datetime.date, datetime.time, datetime.datetime)):
            return value.isoformat()
        elif isinstance(value, array.array):
            return value.tolist()
        else:
            return super().default(value)


logger = logging.getLogger("clickzetta.zettapark")


class WarningHelper:
    def __init__(self, warning_times: int) -> None:
        self.warning_times = warning_times
        self.count = 0

    def warning(self, text: str) -> None:
        if self.count < self.warning_times:
            logger.warning(text)
        self.count += 1


warning_dict: Dict[str, WarningHelper] = {}


def warning(name: str, text: str, warning_times: int = 1) -> None:
    if name not in warning_dict:
        warning_dict[name] = WarningHelper(warning_times)
    warning_dict[name].warning(text)


def func_decorator(
    decorator_type: Literal["deprecated", "experimental", "in private preview"],
    *,
    version: str,
    extra_warning_text: str,
    extra_doc_string: str,
) -> Callable:
    def wrapper(func):
        warning_text = (
            f"{func.__qualname__}() is {decorator_type} since {version}. "
            f"{'Do not use it in production. ' if decorator_type in ('experimental', 'in private preview') else ''}"
            f"{extra_warning_text}"
        )
        doc_string_text = f"This function or method is {decorator_type} since {version}. {extra_doc_string} \n\n"
        func.__doc__ = f"{func.__doc__ or ''}\n\n{' '*8}{doc_string_text}\n"

        @functools.wraps(func)
        def func_call_wrapper(*args, **kwargs):
            warning(func.__qualname__, warning_text)
            return func(*args, **kwargs)

        return func_call_wrapper

    return wrapper


def param_decorator(
    decorator_type: Literal["deprecated", "experimental", "in private preview"],
    *,
    version: str,
) -> Callable:
    def wrapper(param_setter_function):
        warning_text = (
            f"Parameter {param_setter_function.__name__} is {decorator_type} since {version}. "
            f"{'Do not use it in production. ' if decorator_type in ('experimental', 'in private preview') else ''}"
        )

        @functools.wraps(param_setter_function)
        def func_call_wrapper(*args, **kwargs):
            warning(param_setter_function.__name__, warning_text)
            return param_setter_function(*args, **kwargs)

        return func_call_wrapper

    return wrapper


def deprecated(
    *, version: str, extra_warning_text: str = "", extra_doc_string: str = ""
) -> Callable:
    return func_decorator(
        "deprecated",
        version=version,
        extra_warning_text=extra_warning_text,
        extra_doc_string=extra_doc_string,
    )


def experimental(
    *, version: str, extra_warning_text: str = "", extra_doc_string: str = ""
) -> Callable:
    return func_decorator(
        "experimental",
        version=version,
        extra_warning_text=extra_warning_text,
        extra_doc_string=extra_doc_string,
    )


def experimental_parameter(*, version: str) -> Callable:
    return param_decorator(
        "experimental",
        version=version,
    )


def private_preview(
    *, version: str, extra_warning_text: str = "", extra_doc_string: str = ""
) -> Callable:
    return func_decorator(
        "in private preview",
        version=version,
        extra_warning_text=extra_warning_text,
        extra_doc_string=extra_doc_string,
    )


def check_is_pandas_dataframe_in_to_pandas(result: Any) -> None:
    if not isinstance(result, pandas.DataFrame):
        raise ZettaparkClientExceptionMessages.SERVER_FAILED_FETCH_PANDAS(
            "to_pandas() did not return a pandas DataFrame. "
            "If you use session.sql(...).to_pandas(), the input query can only be a "
            "SELECT statement. Or you can use session.sql(...).collect() to get a "
            "list of Row objects for a non-SELECT statement, then convert it to a "
            "pandas DataFrame."
        )


def get_copy_into_table_options(
    options: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    file_format_type_options = options.get("FORMAT_TYPE_OPTIONS", {})
    copy_options = options.get("COPY_OPTIONS", {})
    for k, v in options.items():
        if k in COPY_OPTIONS:
            copy_options[k] = v
        elif k not in NON_FORMAT_TYPE_OPTIONS:
            file_format_type_options[k] = v
    return file_format_type_options, copy_options


# Valid names only contain alphabet characters, numbers and _
TABLE_NAME_PATTERN = "(([a-zA-Z0-9_]+)|(`[a-zA-Z0-9_]+`))"
SINGLE_IDENTIFIER_RE = re.compile("^([a-zA-Z0-9_]+)|(`[a-zA-Z0-9_]+`)$", re.IGNORECASE)
FULL_QUALIFIED_TABLE_NAME_RE = re.compile(
    f"^({TABLE_NAME_PATTERN}\\.){{0,2}}({TABLE_NAME_PATTERN})$"
)


def parse_table_name(table_name: str) -> List[str]:
    if not FULL_QUALIFIED_TABLE_NAME_RE.match(table_name):
        raise ZettaparkClientExceptionMessages.GENERAL_INVALID_OBJECT_NAME(table_name)
    return [x.strip("`") for x in table_name.split(".")]


EMPTY_STRING = ""
BACKTICK = "`"
ALREADY_QUOTED = re.compile(r"^`(?:(?:``)|(?:[^`]))+`$", re.DOTALL)
UNQUOTED_SAFE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
UNQUOTED_SAFE_EXT = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_]*)|(?:`([a-zA-Z_][a-zA-Z0-9_]*)`)$"
)


def quote_name(name: str) -> str:
    if ALREADY_QUOTED.match(name):
        return name.lower()
    return BACKTICK + escape_quotes(name.lower()) + BACKTICK


def escape_quotes(unescaped: str) -> str:
    return unescaped.replace(BACKTICK, BACKTICK + BACKTICK)


def unquote_name(name: str) -> str:
    if ALREADY_QUOTED.match(name):
        return name[1:-1].replace(BACKTICK + BACKTICK, BACKTICK).lower()
    return name.lower()


def unquote_if_safe(name: str) -> str:
    unquoted = unquote_name(name)
    if UNQUOTED_SAFE.match(unquoted) and unquoted not in RESERVED_WORDS:
        return unquoted
    return name


def quote_if_needed(name: str) -> str:
    low = name.lower()
    if UNQUOTED_SAFE.match(low) and low not in RESERVED_WORDS:
        return low
    return quote_name(name)


_TRAILING_SEMICOLON_AND_WHITESPACE = re.compile(r";[;\s]*$")


def trim_trailing_semicolon_and_whitespace(query: str) -> str:
    m = _TRAILING_SEMICOLON_AND_WHITESPACE.search(query)
    if m:
        return query[: m.start()]
    return query
