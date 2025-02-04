import logging
from typing import TYPE_CHECKING, Any, Optional, Tuple, Type

from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
    SettingsConfigDict,
)

from .source import AwsSsmSettingsSource

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient

logger = logging.getLogger(__name__)


class SsmSettingsConfigDict(SettingsConfigDict):
    ssm_prefix: str
    ssm_client: Optional["SSMClient"]


class AwsSsmBaseSettings(BaseSettings):
    """
    Helper to configure the AWS SSM source for Pydantic settings and to pass
    options from init args to settings.
    """

    def __init__(
        self,
        *args,
        _ssm_prefix: Optional[str] = None,
        _ssm_client: Optional["SSMClient"] = None,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            _ssm_prefix: Prefix for all ssm parameters. Must be an absolute path,
            separated by "/". NB:unlike its _env_prefix counterpart, _ssm_prefix
            is treated case sensitively regardless of the _case_sensitive
            parameter value.
            _ssm_client: Optional boto3 SSM client. If not provided, a new client
            will be created.
        """
        # NOTE: Need a direct access to the attributes dictionary to avoid raising an AttributeError: __pydantic_private__ exception
        self.__dict__["__ssm_prefix"] = _ssm_prefix
        self.__dict__["__ssm_client"] = _ssm_client
        super().__init__(self, *args, **kwargs)

    def settings_customise_sources(
        self,
        settings_cls: Type[BaseSettings],
        init_settings: InitSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: SecretsSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        ssm_settings = AwsSsmSettingsSource(
            settings_cls=settings_cls,
            ssm_prefix=self.__dict__["__ssm_prefix"],
            ssm_client=self.__dict__["__ssm_client"],
        )

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            ssm_settings,
        )
