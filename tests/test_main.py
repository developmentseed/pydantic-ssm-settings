from pydantic_ssm_settings import AwsSsmSettingsSource


def test_sanity():
    assert AwsSsmSettingsSource(ssm_prefix="asdf")
