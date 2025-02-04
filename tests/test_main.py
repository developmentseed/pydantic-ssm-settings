import logging
from typing import Tuple, Type

import boto3
import pytest
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pydantic_ssm_settings import AwsSsmSettingsSource

logger = logging.getLogger("pydantic_ssm_settings")
logger.setLevel(logging.DEBUG)


class SimpleSettings(BaseSettings):
    foo: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            AwsSsmSettingsSource(settings_cls),
        )


class IntSettings(BaseSettings):
    foo: str
    bar: int

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            AwsSsmSettingsSource(settings_cls),
        )


# TODO: Bad test, catching wrong valueerror
def test_secrets_dir_must_be_absolute():
    with pytest.raises(ValueError):
        SimpleSettings(
            _ssm_path="asdf",
            _ssm_client=boto3.client("ssm"),
        )


def test_lookup_from_ssm(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="xyz123", Type="String")
    settings = SimpleSettings(
        _ssm_path="/asdf",
        _ssm_client=boto3.client("ssm"),
        _secrets_dir="/fooo",
    )
    assert settings.foo == "xyz123"


def test_prefer_provided(ssm):
    settings = SimpleSettings(_ssm_path="/asdf", foo="manually set")
    assert settings.foo == "manually set"


def test_casting(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="xyz123")
    ssm.put_parameter(Name="/asdf/bar", Value="99")
    settings = IntSettings(_ssm_path="/asdf")
    assert settings.bar == 99
