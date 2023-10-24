import os
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Optional, Union

from botocore.exceptions import ClientError
from botocore.client import Config
import boto3

from pydantic_settings import BaseSettings, EnvSettingsSource

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient


logger = logging.getLogger(__name__)


class AwsSsmSettingsSource(EnvSettingsSource):
    """
    A simple settings source class that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        ssm_prefix: Optional[Union[str, Path]] = None,
        case_sensitive: Optional[bool] = None,
        env_prefix: Optional[str] = None,
        env_nested_delimiter: Optional[str] = None,
    ) -> None:
        self.ssm_prefix = ssm_prefix if ssm_prefix is not None else settings_cls.model_config.get('secrets_dir')
        super().__init__(settings_cls, case_sensitive, env_prefix, env_nested_delimiter)

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_prefix={self.ssm_prefix!r})"

    @property
    def client(self) -> "SSMClient":
        return boto3.client("ssm", config=self.client_config)

    @property
    def client_config(self) -> Config:
        timeout = float(os.environ.get("SSM_TIMEOUT", 0.5))
        return Config(connect_timeout=timeout, read_timeout=timeout)

    def _load_env_vars(self) -> Mapping[str, Optional[str]]:
        logger.debug(f"Building SSM settings with prefix of {str(self.ssm_prefix)}")

        output: Mapping[str, Optional[str]] = {}
        if self.ssm_prefix is None:
            return output

        self.ssm_path = Path(self.ssm_prefix).expanduser()
        if not self.ssm_path.is_absolute():
            raise ValueError("SSM prefix must be absolute path")

        try:
            paginator = self.client.get_paginator("get_parameters_by_path")
            response_iterator = paginator.paginate(
                Path=str(self.ssm_path), WithDecryption=True
            )

            for page in response_iterator:
                for parameter in page["Parameters"]:
                    key = Path(parameter["Name"]).relative_to(self.ssm_path).as_posix()
                    output[key if self.case_sensitive else key.lower()] = parameter["Value"]

        except ClientError:
            logger.exception("Failed to get parameters from %s", str(self.ssm_path))

        return output
