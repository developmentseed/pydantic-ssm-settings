from __future__ import annotations as _annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pydantic import BaseModel
from pydantic._internal._utils import lenient_issubclass
from pydantic.fields import FieldInfo
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

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        """
        Gets the value for field from environment variables and a flag to
        determine whether value is complex.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple contains the key, value if the file exists otherwise `None`, and
                a flag to determine whether value is complex.
        """

        # env_name = /asdf/foo
        # env_vars = {foo:xyz}
        env_val: str | None = None
        for field_key, env_name, value_is_complex in self._extract_field_info(
            field, field_name
        ):
            env_val = self.env_vars.get(env_name)
            if env_val is not None:
                break

        return env_val, field_key, value_is_complex

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            try:
                field_value, field_key, value_is_complex = self.get_field_value(
                    field, field_name
                )
            except Exception as e:
                raise SettingsError(
                    f'error getting value for field "{field_name}" from source "{self.__class__.__name__}"'  # noqa
                ) from e

            try:
                field_value = self.prepare_field_value(
                    field_name, field, field_value, value_is_complex
                )
            except ValueError as e:
                raise SettingsError(
                    f'error parsing value for field "{field_name}" from source "{self.__class__.__name__}"'  # noqa
                ) from e

            if field_value is not None:
                if (
                    not self.case_sensitive
                    and lenient_issubclass(field.annotation, BaseModel)
                    and isinstance(field_value, dict)
                ):
                    data[field_key] = self._replace_field_names_case_insensitively(
                        field, field_value
                    )
                else:
                    data[field_key] = field_value

        return data
