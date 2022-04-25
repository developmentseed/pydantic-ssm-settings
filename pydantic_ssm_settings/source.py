import os
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from botocore.client import Config
import boto3

from pydantic import BaseSettings, typing

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient


logger = logging.getLogger(__name__)


class AwsSsmSettingsSource:
    __slots__ = ("ssm_prefix",)

    def __init__(self, ssm_prefix: Union[typing.StrPath, None]):
        self.ssm_prefix: Union[typing.StrPath, None] = ssm_prefix

    @property
    def client(self) -> "SSMClient":
        return boto3.client("ssm", config=self.client_config)

    @property
    def client_config(self):
        timeout = float(os.environ.get("SSM_TIMEOUT", 0.5))
        return Config(connect_timeout=timeout, read_timeout=timeout)

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

        params = self.client.get_parameters_by_path(
            Path=str(secrets_path), WithDecryption=True
        )["Parameters"]

        return {
            str(Path(param["Name"]).relative_to(secrets_path)): param["Value"]
            for param in params
        }

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_prefix={self.ssm_prefix!r})"
