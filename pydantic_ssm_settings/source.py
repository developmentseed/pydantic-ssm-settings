import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings

from .ssm import lazy_parameter

logger = logging.getLogger(__name__)


class AwsSsmSettingsSource:
    __slots__ = ("ssm_prefix",)

    def __init__(self, ssm_prefix):
        self.ssm_prefix: Union[Path, str, None] = ssm_prefix

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        """
        Returns lazy SSM values for all settings.
        """
        secrets: Dict[str, Optional[Any]] = {}

        if self.ssm_prefix is None:
            return secrets

        secrets_path = Path(self.ssm_prefix)

        if not secrets_path.is_absolute():
            raise ValueError("SSM prefix must be absolute path")

        logger.debug(f"Building SSM settings with prefix of {secrets_path=}")

        for field in settings.__fields__.values():
            for env_name in field.field_info.extra["env_names"]:
                secrets[field.alias] = lazy_parameter(path=(secrets_path / env_name), field=field)
        return secrets

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_prefix={self.ssm_prefix!r})"
