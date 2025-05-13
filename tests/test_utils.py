from datetime import datetime, timezone
from typing import Optional
from arize_toolkit.utils import parse_datetime, _convert_to_dict
from pydantic import BaseModel
from enum import Enum
import pytest


class SampleEnum(Enum):
    TEST0 = ("test0", "TEST0")
    TEST1 = ("test1", "TEST1")
    TEST2 = ("test2", "TEST2")


class SampleModel(BaseModel):
    name: str
    age: int
    date: datetime
    num: SampleEnum
    dictionary: dict[str, int]
    nested: Optional[BaseModel]


class SampleModel1(BaseModel):
    name: str
    age: int
    date: datetime
    num: SampleEnum
    dictionary: dict[str, int]
    nested: Optional[SampleModel]


class SampleModel2(BaseModel):
    name: str
    age: int
    date: datetime
    num: SampleEnum
    dictionary: dict[str, int]
    nested: Optional[SampleModel1]


@pytest.fixture
def model0():
    return SampleModel(
        name="test",
        age=10,
        num=SampleEnum.TEST0,
        date=datetime(2024, 4, 12, 12, 0, 0, 123456, tzinfo=timezone.utc),
        dictionary={"test": 0},
        nested=None,
    )


@pytest.fixture
def model1(model0):
    return SampleModel1(
        name="test1",
        age=100,
        dictionary={"test": 1},
        date=datetime(2024, 4, 12, 12, 0, 0, 123456, tzinfo=timezone.utc),
        num=SampleEnum.TEST1,
        nested=model0,
    )


@pytest.fixture
def model2(model1):
    return SampleModel2(
        name="test2",
        age=1000,
        dictionary={"test": 2},
        date=datetime(2024, 4, 12, 12, 0, 0, 123456, tzinfo=timezone.utc),
        num=SampleEnum.TEST2,
        nested=model1,
    )


class TestConvertToDictTest:
    def test_convert_to_dict_0(self, model0):
        expected_model0 = {
            "name": "test",
            "age": 10,
            "date": "2024-04-12T12:00:00.123456Z",
            "num": "TEST0",
            "dictionary": {"test": 0},
            "nested": None,
        }
        result = _convert_to_dict(model0)
        print(result)
        assert result == expected_model0

    def test_convert_to_dict_1(self, model1, model0):
        model_0 = _convert_to_dict(model0)
        print(model_0)
        expected_model1 = {
            "name": "test1",
            "age": 100,
            "date": "2024-04-12T12:00:00.123456Z",
            "num": "TEST1",
            "dictionary": {"test": 1},
            "nested": model_0,
        }
        result = _convert_to_dict(model1)
        print(result)
        assert result == expected_model1

    def test_convert_to_dict_2(self, model2, model1):
        model_1 = _convert_to_dict(model1)
        expected_model2 = {
            "name": "test2",
            "age": 1000,
            "date": "2024-04-12T12:00:00.123456Z",
            "num": "TEST2",
            "dictionary": {"test": 2},
            "nested": model_1,
        }
        result = _convert_to_dict(model2)
        print(result)
        assert result == expected_model2


class TestParseDatetimeTest:
    def test_parse_datetime(self):
        assert parse_datetime("2023-04-01T12:30:45Z") == datetime(
            2023, 4, 1, 12, 30, 45, tzinfo=timezone.utc
        )
        assert parse_datetime("04/01/2023 12:30:45") == datetime(
            2023, 4, 1, 12, 30, 45, tzinfo=timezone.utc
        )
        assert parse_datetime("2023-04-01 12:30:45") == datetime(
            2023, 4, 1, 12, 30, 45, tzinfo=timezone.utc
        )
        assert parse_datetime("04/01/2023 12:30") == datetime(
            2023, 4, 1, 12, 30, tzinfo=timezone.utc
        )
        assert parse_datetime("2023-04-01") == datetime(2023, 4, 1, tzinfo=timezone.utc)
        assert parse_datetime("04/01/2023") == datetime(2023, 4, 1, tzinfo=timezone.utc)
        assert parse_datetime("2023-04-01 12:30") == datetime(
            2023, 4, 1, 12, 30, tzinfo=timezone.utc
        )
        assert parse_datetime("2023-04-01 12:30:45.123Z") == datetime(
            2023, 4, 1, 12, 30, 45, 123000, tzinfo=timezone.utc
        )
        assert parse_datetime("2023-04-01 12:30:45.123+00:00") == datetime(
            2023, 4, 1, 12, 30, 45, 123000, tzinfo=timezone.utc
        )
        assert parse_datetime("2023-04-01 12:30:45.123-00:00") == datetime(
            2023, 4, 1, 12, 30, 45, 123000, tzinfo=timezone.utc
        )
        assert parse_datetime(1712923200) == datetime(
            2024, 4, 12, 12, 0, 0, tzinfo=timezone.utc
        )
        assert parse_datetime(1712923200.123) == datetime(
            2024, 4, 12, 12, 0, 0, 123000, tzinfo=timezone.utc
        )
        assert parse_datetime(1712923200.123456) == datetime(
            2024, 4, 12, 12, 0, 0, 123456, tzinfo=timezone.utc
        )
        assert parse_datetime(1712923200.123456789) == datetime(
            2024, 4, 12, 12, 0, 0, 123457, tzinfo=timezone.utc
        )
        assert parse_datetime(datetime(2024, 4, 12, 12, 0, 0, 123456)) == datetime(
            2024, 4, 12, 12, 0, 0, 123456
        )

    def test_parse_datetime_errors(self):
        with pytest.raises(
            ValueError, match="Invalid datetime string, could not parse: abc"
        ):
            parse_datetime("abc")

        with pytest.raises(
            ValueError, match="Invalid datetime string, could not parse: 12.2024.10"
        ):
            parse_datetime("12.2024.10")

        with pytest.raises(
            ValueError, match="Invalid datetime string, could not parse: 12/2024/10"
        ):
            parse_datetime("12/2024/10")

        with pytest.raises(
            ValueError, match="Invalid datetime string, could not parse: 12-2024-10"
        ):
            parse_datetime("12-2024-10")
