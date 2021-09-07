from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings


class LazySsm:
    __slots__ = ("path",)

    def __init__(self, path: Path):
        self.path: Union[Path, str, None] = path

    def __repr__(self):
        return "TODO:"


class AwsSsmSettingsSource:
    __slots__ = ("ssm_prefix",)

    def __init__(self, ssm_prefix):
        self.ssm_prefix: Union[Path, str, None] = ssm_prefix

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        """
        Returns lazy SSM values for all settings.
        """
        secrets: Dict[str, Optional[LazySsm]] = {}

        if self.ssm_prefix is None:
            return secrets

        secrets_path = Path(self.ssm_prefix)

        for field in settings.__fields__.values():
            for env_name in field.field_info.extra["env_names"]:
                path = secrets_path / env_name
                secrets[field.alias] = LazySsm(path)
        return secrets

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(init_kwargs={self.ssm_prefix!r})"
