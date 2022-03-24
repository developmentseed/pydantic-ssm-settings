import logging
from functools import cached_property
from pathlib import Path
from typing import Any

import boto3
import botocore

from pydantic.fields import ModelField

logger = logging.getLogger(__name__)


def lazy_parameter(path: Path, field: ModelField) -> Any:  # noqa: C901
    """
    Generate a stand-in config object to lazy-load a value from SSM Parameter Store.
    """
    # Dynamically inherit from field type to pass Pydantic's type checks
    class LazyParameter(field.type_):  # type: ignore
        # Heavily inspired by https://github.com/mitsuhiko/speaklater

        @cached_property
        def value(self) -> Any:
            logger.debug(f"Fetching {path}")
            client = boto3.client("ssm")
            try:
                response = client.get_parameter(Name=str(path), WithDecryption=True)
            except botocore.exceptions.ClientError as error:
                if (error.response['Error']['Code'] == 'ParameterNotFound'):
                    return field.default
                else:
                    raise error
            value = response["Parameter"]["Value"]
            return field.type_(value)

        def __repr__(self):  # type: ignore
            return repr(self.value)

        def __contains__(self, key):  # type: ignore
            return key in self.value

        def __nonzero__(self):  # type: ignore
            return bool(self.value)

        def __dir__(self):  # type: ignore
            return dir(self.value)

        def __iter__(self):  # type: ignore
            return iter(self.value)

        def __len__(self):  # type: ignore
            return len(self.value)

        def __str__(self):  # type: ignore
            return str(self.value)

        def __unicode__(self):  # type: ignore
            return self.value

        def __add__(self, other):  # type: ignore
            return self.value + other

        def __radd__(self, other):  # type: ignore
            return other + self.value

        def __mod__(self, other):  # type: ignore
            return self.value % other

        def __rmod__(self, other):  # type: ignore
            return other % self.value

        def __mul__(self, other):  # type: ignore
            return self.value * other

        def __rmul__(self, other):  # type: ignore
            return other * self.value

        def __lt__(self, other):  # type: ignore
            return self.value < other

        def __le__(self, other):  # type: ignore
            return self.value <= other

        def __eq__(self, other):  # type: ignore
            return self.value == other

        def __ne__(self, other):  # type: ignore
            return self.value != other

        def __gt__(self, other):  # type: ignore
            return self.value > other

        def __ge__(self, other):  # type: ignore
            return self.value >= other

        def __getattr__(self, name):  # type: ignore
            if name == "__members__":
                return self.__dir__()  # type: ignore
            return getattr(self.value, name)

        def __getstate__(self):  # type: ignore
            return self._func, self._args, self._kwargs

        def __setstate__(self, tup):  # type: ignore
            self._func, self._args, self._kwargs = tup

        def __getitem__(self, key):  # type: ignore
            return self.value[key]

    return LazyParameter()
