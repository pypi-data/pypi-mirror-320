"""A Python client wrapping up HashiCorp's Terraform Cloud API."""

from importlib import metadata

from .api import *  # noqa
from .client import *  # noqa


__version__ = metadata.version("noos-tf")
