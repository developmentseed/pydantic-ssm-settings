import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional

from pydantic_settings.sources import EnvSettingsSource

if TYPE_CHECKING:
    try:
        from mypy_boto3_ssm import SSMClient
    except ImportError:
        ...


class AwsSsmSettingsSource(EnvSettingsSource):
    DEFAULT_SSM_Path = "/"

    def __call__(self) -> Dict[str, Any]:
        return super().__call__()

    def _get_source_arg(self, name: str) -> Any:
        """
        Helper to retrieve source arguments from the settings class or the current state.
        """
        return next(
            (
                val
                for val in [
                    self.settings_cls.model_config.get(name),
                    self.current_state.get(f"_{name}"),
                ]
                if val
            ),
            None,
        )

    @property
    def _ssm_client(self) -> "SSMClient":
        client = self._get_source_arg("ssm_client")
        if client is None:
            raise ValueError(
                f"Required configuration 'ssm_client' not set on {self.__class__.__name__}"
            )
        return client

    @property
    def _ssm_path(self) -> str:
        return self._get_source_arg("ssm_path") or self.DEFAULT_SSM_Path

    # def get_field_value(
    #     self, field: FieldInfo, field_name: str
    # ) -> Tuple[Any, str, bool]: ...

    def _load_env_vars(self) -> Mapping[str, Optional[str]]:
        paginator = self._ssm_client.get_paginator("get_parameters_by_path")
        response_iterator = paginator.paginate(
            Path=self._ssm_path, WithDecryption=True, Recursive=True
        )

        output = {}
        try:
            for page in response_iterator:
                for parameter in page["Parameters"]:
                    name = Path(parameter["Name"])
                    key = name.relative_to(self._ssm_path).as_posix()

                    if not self.case_sensitive:
                        first_key, *rest = key.split(self.env_nested_delimiter)
                        key = self.env_nested_delimiter.join([first_key.lower(), *rest])

                    output[key] = parameter["Value"]

        except self._ssm_client.exceptions.ClientError as e:
            warnings.warn(f"Unable to get parameters from {self._ssm_path!r}: {e}")

        return output

    def __repr__(self) -> str:
        return f"AwsSsmSettingsSource(ssm_path={self._ssm_path!r}, ssm_client={self._ssm_client!r})"
