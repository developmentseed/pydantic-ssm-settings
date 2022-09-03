import logging
from typing import Tuple

from pydantic.env_settings import (
    EnvSettingsSource,
    InitSettingsSource,
    SecretsSettingsSource,
    SettingsSourceCallable,
)

from .source import AwsSsmSettingsSource

logger = logging.getLogger(__name__)


class AwsSsmSourceConfig:
    @classmethod
    def customise_sources(
        cls,
        init_settings: InitSettingsSource,
        env_settings: EnvSettingsSource,
        file_secret_settings: SecretsSettingsSource,
    ) -> Tuple[SettingsSourceCallable, ...]:

        ssm_settings = AwsSsmSettingsSource(
            ssm_prefix=file_secret_settings.secrets_dir,
            env_nested_delimiter=env_settings.env_nested_delimiter,
        )

        return (
            init_settings,
            env_settings,
            # Usurping the `secrets_dir` arg. We can't expect any other args to
            # be passed to # the Settings module because Pydantic will complain
            # about unexpected arguments. `secrets_dir` comes from `_secrets_dir`,
            # one of the few special kwargs that Pydantic will allow:
            # https://github.com/samuelcolvin/pydantic/blob/45db4ad3aa558879824a91dd3b011d0449eb2977/pydantic/env_settings.py#L33
            ssm_settings,
        )
