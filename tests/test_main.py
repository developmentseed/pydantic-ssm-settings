import boto3
import moto
import pytest
from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from pydantic_ssm_settings import SsmBaseSettings, SsmSettingsConfigDict


class SimpleSettings(SsmBaseSettings):
    foo: str


class IntSettings(SsmBaseSettings):
    foo: str
    bar: int


class ChildSetting(BaseModel):
    bar: str


class ParentSetting(SsmBaseSettings):
    foo: ChildSetting


def test_ssm_prefix_must_be_absolute():
    with pytest.raises(ValueError):
        SimpleSettings(_ssm_prefix="asdf")


def test_lookup_from_ssm(ssm):
    ssm.put_parameter(Name="/foo", Value="bar", Type="String")
    settings = SimpleSettings()
    assert settings.foo == "bar"


def test_lookup_from_ssm_with_prefix(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="bar", Type="String")
    settings = SimpleSettings(_ssm_prefix="/asdf")
    assert settings.foo == "bar"


def test_casting(ssm):
    ssm.put_parameter(Name="/foo", Value="xyz123", Type="String")
    ssm.put_parameter(Name="/bar", Value="99", Type="String")
    settings = IntSettings()
    assert isinstance(settings.bar, int)
    assert settings.bar == 99


def test_parameter_override(ssm):
    ssm.put_parameter(Name="/foo", Value="ssm_bar", Type="String")
    s = SimpleSettings(foo="param_bar")
    assert s.foo == "param_bar"


def test_dotenv_override(tmp_path, ssm):
    ssm.put_parameter(Name="/foo", Value="ssm_bar", Type="String")
    p = tmp_path / ".env"
    p.write_text("foo=dotenv_bar")

    s = SimpleSettings(_env_file=p)
    assert s.foo == "dotenv_bar"


def test_env_override(env, ssm):
    ssm.put_parameter(Name="/foo", Value="ssm_bar", Type="String")
    env.set("foo", "env_bar")
    s = SimpleSettings()
    assert s.foo == "env_bar"


def test_secret_override(tmp_path, ssm):
    p = tmp_path / "foo"
    p.write_text("secret_bar")
    ssm.put_parameter(Name="/foo", Value="ssm_bar", Type="String")
    s = SimpleSettings(_secrets_dir=tmp_path)
    assert s.foo == "secret_bar"


def test_nested_parameters(ssm):
    ssm.put_parameter(Name="/foo/bar", Value="bar_value", Type="String")
    settings = ParentSetting()
    assert settings.foo.bar == "bar_value"


def test_ssm_parameter_json(ssm):
    ssm.put_parameter(Name="/foo", Value='{"bar": "xyz123"}', Type="String")
    settings = ParentSetting()
    assert settings.foo.bar == "xyz123"


def test_ssm_parameter_json_override(ssm):
    ssm.put_parameter(Name="/foo", Value='{"bar": "xyz123"}', Type="String")
    ssm.put_parameter(Name="/foo/bar", Value="overwritten", Type="String")
    settings = ParentSetting()
    assert settings.foo.bar == "overwritten"


class CaseInsensitiveSettings(SsmBaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)
    foo: str


def test_case_insensitivity(ssm):
    ssm.put_parameter(Name="/FOO", Value="bar", Type="String")
    settings = CaseInsensitiveSettings()
    assert settings.foo == "bar"


class CustomConfigDict(SsmBaseSettings):
    model_config = SsmSettingsConfigDict(ssm_prefix="/asdf")
    foo: str


def test_parameters_from_model_config(ssm):
    ssm.put_parameter(Name="/asdf/foo", Value="bar", Type="String")
    settings = CustomConfigDict()
    assert settings.foo == "bar"


@pytest.mark.parametrize("region", ["us-east-1", "us-west-2"])
def test_custom_client(region: str):
    with moto.mock_aws():
        client = boto3.client("ssm", region_name=region)
        client.put_parameter(Name="/foo", Value=region, Type="String")

        settings = SimpleSettings(_ssm_client=client)
        assert settings.foo == region
