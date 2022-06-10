import os
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from botocore.exceptions import ClientError
from botocore.client import Config
import boto3

from pydantic import BaseSettings, typing

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient


logger = logging.getLogger(__name__)


class AwsSsmSettingsSource:
    __slots__ = ("ssm_prefix",)

    def __init__(self, ssm_prefix: Optional[typing.StrPath]):
        self.ssm_prefix: Optional[typing.StrPath] = ssm_prefix

    @property
    def client(self) -> "SSMClient":
        return boto3.client("ssm", config=self.client_config)

    @property
    def client_config(self) -> Config:
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

        try:
            paginator = self.client.get_paginator("get_parameters_by_path")
            response_iterator = paginator.paginate(
                Path=str(secrets_path), WithDecryption=True
            )

            output = {}
            for page in response_iterator:
                for parameter in page["Parameters"]:
                    key = (
                        Path(parameter["Name"])
                        .relative_to(secrets_path)
                        .as_posix()
                    )
                    output[key] = parameter["Value"]
            return output

        except ClientError:
            logger.exception("Failed to get parameters from %s", secrets_path)
            return {}

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_prefix={self.ssm_prefix!r})"
