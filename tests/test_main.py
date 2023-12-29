import logging

import pytest
from pydantic import (
    BaseModel,
)
from pydantic_settings import SettingsConfigDict

from pydantic_ssm_settings import (
    AwsSsmSourceConfig,
    SsmSettingsConfigDict,
)

logger = logging.getLogger("pydantic_ssm_settings")
logger.setLevel(logging.DEBUG)


class SimpleSettings(AwsSsmSourceConfig):
    foo: str


class IntSettings(AwsSsmSourceConfig):
    foo: str
    bar: int


class ChildSetting(BaseModel):
    bar: str


class ParentSetting(AwsSsmSourceConfig):
    foo: ChildSetting


def test_ssm_prefix_must_be_absolute():
    with pytest.raises(ValueError):
        SimpleSettings(_ssm_prefix="asdf")


def test_lookup_from_ssm(ssm):
    ssm.put_parameter(Name="/foo", Value="bar")
    settings = SimpleSettings()
    assert settings.foo == "bar"


def test_lookup_from_ssm_with_prefix(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="bar")
    settings = SimpleSettings(_ssm_prefix="/asdf")
    assert settings.foo == "bar"


def test_casting(ssm):
    ssm.put_parameter(Name="/foo", Value="xyz123")
    ssm.put_parameter(Name="/bar", Value="99")
    settings = IntSettings()
    assert isinstance(settings.bar, int)
    assert settings.bar == 99


def test_parameter_override(ssm):
    ssm.put_parameter(Name="/foo", Value="ssm_bar")
    s = SimpleSettings(foo="param_bar")
    assert s.foo == "param_bar"


def test_dotenv_override(tmp_path, ssm):
    ssm.put_parameter(Name="/foo", Value="ssm_bar")
    p = tmp_path / ".env"
    p.write_text("foo=dotenv_bar")

    s = SimpleSettings(_env_file=p)
    assert s.foo == "dotenv_bar"


def test_env_override(env, ssm):
    ssm.put_parameter(Name="/foo", Value="ssm_bar")
    env.set("foo", "env_bar")
    s = SimpleSettings()
    assert s.foo == "env_bar"


def test_secret_override(tmp_path, ssm):
    p = tmp_path / "foo"
    p.write_text("secret_bar")
    ssm.put_parameter(Name="/foo", Value="ssm_bar")
    s = SimpleSettings(_secrets_dir=tmp_path)
    assert s.foo == "secret_bar"


def test_nested_parameters(ssm):
    ssm.put_parameter(Name="/foo/bar", Value="bar_value")
    settings = ParentSetting()
    assert settings.foo.bar == "bar_value"


def test_ssm_parameter_json(ssm):
    ssm.put_parameter(Name="/foo", Value='{"bar": "xyz123"}')
    settings = ParentSetting()
    assert settings.foo.bar == "xyz123"


def test_ssm_parameter_json_override(ssm):
    ssm.put_parameter(Name="/foo", Value='{"bar": "xyz123"}')
    ssm.put_parameter(Name="/foo/bar", Value="overwritten")
    settings = ParentSetting()
    assert settings.foo.bar == "overwritten"


class CaseInsensitiveSettings(AwsSsmSourceConfig):
    model_config = SettingsConfigDict(case_sensitive=False)
    foo: str


def test_case_insensitivity(ssm):
    ssm.put_parameter(Name="/FOO", Value="bar")
    settings = CaseInsensitiveSettings()
    assert settings.foo == "bar"


class CustomConfigDict(AwsSsmSourceConfig):
    model_config = SsmSettingsConfigDict(ssm_prefix="/asdf")
    foo: str


def test_parameters_from_model_config(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="bar")
    settings = CustomConfigDict()
    assert settings.foo == "bar"
