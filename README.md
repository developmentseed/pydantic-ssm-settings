# pydantic-ssm-settings

Integrate [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) with [Pydantic Settings](https://github.com/pydantic/pydantic-settings).

## Usage

The simplest way to use this module is to inhert your settings from `SsmBaseSettings`. This add the `SsmSettingsSource` as a custom settings source and enabled passing source configuration (e.g. `_ssm_prefix`, `_ssm_client`) via `kwargs` when initializing a settings class.

```py
from pydantic_ssm_settings import SsmBaseSettings


class WebserviceSettings(SsmBaseSettings):
    some_val: str
    another_val: int

WebserviceSettings(_ssm_prefix="/prod/webservice")
```

Alternatively, configuration may be specified within the settings class via [`BaseModel.model_config`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_config):

```py
from pydantic_ssm_settings import SsmSettingsConfigDict

class WebserviceSettings(SsmBaseSettings):
    model_config = SsmSettingsConfigDict(ssm_prefix="/prod/webservice")
    some_val: str
    another_val: int


WebserviceSettings()
```

If it is preferred to avoid altering the baseclass of a settings model, the source can be manually added and configured as such:

```py
from typing import Tuple, Type
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
)
from pydantic_ssm_settings import SsmSettingsConfigDict, SsmSettingsSource

class WebserviceSettings(BaseSettings):
    model_config = SsmSettingsConfigDict(ssm_prefix="/asdf")
    foo: str

    def settings_customise_sources(
        self,
        settings_cls: Type[BaseSettings],
        init_settings: InitSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: SecretsSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            SsmSettingsSource(settings_cls),
        )
```
