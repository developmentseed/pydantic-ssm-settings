import logging
from functools import cached_property

import boto3

logger = logging.getLogger(__name__)


def lazy_parameter(path, field):  # noqa: C901
    """
    Generate a stand-in config object to lazy-load a value from SSM Parameter Store.
    """
    # Dynamically inherit from field type to pass Pydantic's type checks
    class LazyParameter(field.type_):
        # Heavily inspired by https://github.com/mitsuhiko/speaklater

        @cached_property
        def value(self):
            logger.debug(f"Fetching {path}")
            client = boto3.client("ssm")
            # TODO: Fallback to field default if no value is available...
            response = client.get_parameter(Name=str(path), WithDecryption=True)
            value = response["Parameter"]["Value"]
            return field.type_(value)

        def __repr__(self):
            return repr(self.value)

        def __contains__(self, key):
            return key in self.value

        def __nonzero__(self):
            return bool(self.value)

        def __dir__(self):
            return dir(self.value)

        def __iter__(self):
            return iter(self.value)

        def __len__(self):
            return len(self.value)

        def __str__(self):
            return str(self.value)

        def __unicode__(self):
            return self.value

        def __add__(self, other):
            return self.value + other

        def __radd__(self, other):
            return other + self.value

        def __mod__(self, other):
            return self.value % other

        def __rmod__(self, other):
            return other % self.value

        def __mul__(self, other):
            return self.value * other

        def __rmul__(self, other):
            return other * self.value

        def __lt__(self, other):
            return self.value < other

        def __le__(self, other):
            return self.value <= other

        def __eq__(self, other):
            return self.value == other

        def __ne__(self, other):
            return self.value != other

        def __gt__(self, other):
            return self.value > other

        def __ge__(self, other):
            return self.value >= other

        def __getattr__(self, name):
            if name == "__members__":
                return self.__dir__()
            return getattr(self.value, name)

        def __getstate__(self):
            return self._func, self._args, self._kwargs

        def __setstate__(self, tup):
            self._func, self._args, self._kwargs = tup

        def __getitem__(self, key):
            return self.value[key]

    return LazyParameter()
