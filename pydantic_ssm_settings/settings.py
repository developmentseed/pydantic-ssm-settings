import logging
from typing import Tuple

from pydantic.env_settings import SettingsSourceCallable

from .source import AwsSsmSettingsSource

logger = logging.getLogger(__name__)


class AwsSsmSourceConfig:
    @classmethod
    def customise_sources(
        cls,
        init_settings: SettingsSourceCallable,
        env_settings: SettingsSourceCallable,
        file_secret_settings: SettingsSourceCallable,
    ) -> Tuple[SettingsSourceCallable, ...]:

        return (
            env_settings,
            init_settings,
            # Usurping the `secrets_dir` arg. We can't expect any other args to
            # be passed to # the Settings module because Pydantic will complain
            # about unexpected arguments. `secrets_dir` comes from `_secrets_dir`,
            # one of the few special kwargs that Pydantic will allow:
            # https://github.com/samuelcolvin/pydantic/blob/45db4ad3aa558879824a91dd3b011d0449eb2977/pydantic/env_settings.py#L33
            AwsSsmSettingsSource(ssm_prefix=file_secret_settings.secrets_dir),
        )
