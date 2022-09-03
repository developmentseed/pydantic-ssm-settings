import os
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Tuple

from botocore.exceptions import ClientError
from botocore.client import Config
import boto3

from pydantic import BaseSettings
from pydantic.typing import StrPath, get_origin, is_union
from pydantic.utils import deep_update
from pydantic.fields import ModelField

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient


logger = logging.getLogger(__name__)


class SettingsError(ValueError):
    pass


class AwsSsmSettingsSource:
    __slots__ = ("ssm_prefix", "env_nested_delimiter")

    def __init__(
        self,
        ssm_prefix: Optional[StrPath],
        env_nested_delimiter: Optional[str] = None,
    ):
        self.ssm_prefix: Optional[StrPath] = ssm_prefix
        self.env_nested_delimiter: Optional[str] = env_nested_delimiter

    @property
    def client(self) -> "SSMClient":
        return boto3.client("ssm", config=self.client_config)

    @property
    def client_config(self) -> Config:
        timeout = float(os.environ.get("SSM_TIMEOUT", 0.5))
        return Config(connect_timeout=timeout, read_timeout=timeout)

    def load_from_ssm(self, secrets_path: Path, case_sensitive: bool):

        if not secrets_path.is_absolute():
            raise ValueError("SSM prefix must be absolute path")

        logger.debug(f"Building SSM settings with prefix of {secrets_path=}")

        output = {}
        try:
            paginator = self.client.get_paginator("get_parameters_by_path")
            response_iterator = paginator.paginate(
                Path=str(secrets_path), WithDecryption=True
            )

            for page in response_iterator:
                for parameter in page["Parameters"]:
                    key = Path(parameter["Name"]).relative_to(secrets_path).as_posix()
                    output[key if case_sensitive else key.lower()] = parameter["Value"]

        except ClientError:
            logger.exception("Failed to get parameters from %s", secrets_path)

        return output

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        """
        Returns lazy SSM values for all settings.
        """
        d: Dict[str, Optional[Any]] = {}

        if self.ssm_prefix is None:
            return d

        ssm_values = self.load_from_ssm(
            secrets_path=Path(self.ssm_prefix),
            case_sensitive=settings.__config__.case_sensitive,
        )

        # The following was lifted directly from https://github.com/samuelcolvin/pydantic/blob/a21f0763ee877f0c86f254a5d60f70b1002faa68/pydantic/env_settings.py#L165-L237  # noqa
        for field in settings.__fields__.values():
            env_val: Optional[str] = None
            for env_name in field.field_info.extra["env_names"]:
                env_val = ssm_values.get(env_name)
                if env_val is not None:
                    break

            is_complex, allow_json_failure = self.field_is_complex(field)
            if is_complex:
                if env_val is None:
                    # field is complex but no value found so far, try explode_env_vars
                    env_val_built = self.explode_ssm_values(field, ssm_values)
                    if env_val_built:
                        d[field.alias] = env_val_built
                else:
                    # field is complex and there's a value, decode that as JSON, then
                    # add explode_env_vars
                    try:
                        env_val = settings.__config__.json_loads(env_val)
                    except ValueError as e:
                        if not allow_json_failure:
                            raise SettingsError(
                                f'error parsing JSON for "{env_name}"'
                            ) from e

                    if isinstance(env_val, dict):
                        d[field.alias] = deep_update(
                            env_val, self.explode_ssm_values(field, ssm_values)
                        )
                    else:
                        d[field.alias] = env_val
            elif env_val is not None:
                # simplest case, field is not complex, we only need to add the 
                # value if it was found
                d[field.alias] = env_val

        return d

    def field_is_complex(self, field: ModelField) -> Tuple[bool, bool]:
        """
        Find out if a field is complex, and if so whether JSON errors should be ignored
        """
        if field.is_complex():
            allow_json_failure = False
        elif (
            is_union(get_origin(field.type_))
            and field.sub_fields
            and any(f.is_complex() for f in field.sub_fields)
        ):
            allow_json_failure = True
        else:
            return False, False

        return True, allow_json_failure

    def explode_ssm_values(
        self, field: ModelField, env_vars: Mapping[str, Optional[str]]
    ) -> Dict[str, Any]:
        """
        Process env_vars and extract the values of keys containing 
        env_nested_delimiter into nested dictionaries.

        This is applied to a single field, hence filtering by env_var prefix.
        """
        prefixes = [
            f"{env_name}{self.env_nested_delimiter}"
            for env_name in field.field_info.extra["env_names"]
        ]
        result: Dict[str, Any] = {}
        for env_name, env_val in env_vars.items():
            if not any(env_name.startswith(prefix) for prefix in prefixes):
                continue
            _, *keys, last_key = env_name.split(self.env_nested_delimiter)
            env_var = result
            for key in keys:
                env_var = env_var.setdefault(key, {})
            env_var[last_key] = env_val

        return result

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_prefix={self.ssm_prefix!r})"
