# pydantic-ssm-settings

Replace Pydantic's builtin secret support [Secret Support](https://pydantic-docs.helpmanual.io/usage/settings/#secret-support) with an implementation that loads parameters from [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). Parameters are loaded _lazily_, meaning that they are only requested from AWS if they are not provided via [standard field value priority](https://pydantic-docs.helpmanual.io/usage/settings/#field-value-priority) (i.e. initialiser, environment variable, or via `.env` file).

## Usage

The simplest way to use this module is to inhert your settings `Config` class from `AwsSsmSourceConfig`. This will overwrite the [`file_secret_settings` settings source](https://pydantic-docs.helpmanual.io/usage/settings/#customise-settings-sources) with the `AwsSsmSettingsSource`. Provide a prefix to SSM parameters via the `_secrets_dir` initialiser value or the `secrets_dir` Config value.

```py
from pydantic import BaseSettings
from pydantic_ssm_settings import AwsSsmSourceConfig


class WebserviceSettings(BaseSettings):
    some_val: str
    another_val: int

    class Config(AwsSsmSourceConfig):
        ...

SimpleSettings(_secrets_dir='/prod/webservice')
```

The above example will attempt to retreive values from `/prod/webservice/some_val` and `/prod/webservice/another_val` if not provided otherwise.