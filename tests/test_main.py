import logging

import pytest

from pydantic import BaseSettings
from pydantic_ssm_settings import AwsSsmSourceConfig

logger = logging.getLogger("pydantic_ssm_settings")
logger.setLevel(logging.DEBUG)


class SimpleSettings(BaseSettings):
    foo: str

    class Config(AwsSsmSourceConfig):
        ...


class IntSettings(BaseSettings):
    foo: str
    bar: int

    class Config(AwsSsmSourceConfig):
        ...


def test_secrets_dir_must_be_absolute():
    with pytest.raises(ValueError):
        SimpleSettings(_secrets_dir="asdf")


def test_lookup_from_ssm(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="xyz123")
    settings = SimpleSettings(_secrets_dir="/asdf")
    assert settings.foo == "xyz123"


def test_prefer_provided(ssm):
    settings = SimpleSettings(_secrets_dir="/asdf", foo="manually set")
    assert settings.foo == "manually set"


def test_casting(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="xyz123")
    ssm.put_parameter(Name="/asdf/bar", Value="99")
    settings = IntSettings(_secrets_dir="/asdf")
    assert settings.bar == 99
