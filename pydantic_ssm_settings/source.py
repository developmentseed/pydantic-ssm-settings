from __future__ import annotations as _annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings
from pydantic_settings.sources import EnvSettingsSource

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient


logger = logging.getLogger(__name__)


class SettingsError(ValueError):
    pass


class AwsSsmSettingsSource(EnvSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        case_sensitive: Optional[bool] = None,
        ssm_prefix: Optional[str] = None,
        ssm_client: Optional["SSMClient"] = None,
    ):
        ssm_prefix = (
            ssm_prefix
            if ssm_prefix is not None
            else settings_cls.model_config.get("ssm_prefix", "/")
        )
        self.ssm_client = (
            ssm_client
            if ssm_client
            else settings_cls.model_config.get("ssm_client", self._build_client())
        )
        super().__init__(
            settings_cls,
            case_sensitive=case_sensitive,
            env_prefix=ssm_prefix,
            env_nested_delimiter="/",  # SSM only accepts / as a delimiter
        )
        assert ssm_prefix == self.env_prefix

    def _build_client(self) -> "SSMClient":
        timeout = float(os.environ.get("SSM_TIMEOUT", 0.5))
        return boto3.client(
            "ssm", config=Config(connect_timeout=timeout, read_timeout=timeout)
        )

    def _load_env_vars(
        self,
    ):
        # NOTE: env_prefix represents the ssm_prefix
        if not Path(self.env_prefix).is_absolute():
            raise ValueError("SSM prefix must be absolute path")

        logger.debug(f"Building SSM settings with prefix of {self.env_prefix=}")

        output = {}
        try:
            paginator = self.ssm_client.get_paginator("get_parameters_by_path")
            response_iterator = paginator.paginate(
                Path=self.env_prefix, WithDecryption=True, Recursive=True
            )

            for page in response_iterator:
                for parameter in page["Parameters"]:
                    key = (
                        Path(parameter["Name"]).relative_to(self.env_prefix).as_posix()
                    )
                    output[
                        (
                            self.env_prefix + key
                            if self.case_sensitive
                            else self.env_prefix.lower() + key.lower()
                        )
                    ] = parameter["Value"]

        except ClientError:
            logger.exception("Failed to get parameters from %s", self.env_prefix)

        return output

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_prefix={self.env_prefix!r})"
