"""This module implements the yet_another_wizz (yaw) commandline interface.
"""

from yaw_cli import commandline, pipeline
from yaw_cli.commandline import Commandline
from yaw_cli.pipeline.logger import init_logger
from yaw_cli.pipeline.project import ProjectDirectory

__all__ = ["Commandline", "ProjectDirectory", "commandline", "pipeline", "init_logger"]
__version__ = "1.3.0"


import warnings

warnings.warn(
    "The 'yaw_cli' module is deprecated, please migrate to the simplifed commandline client shipped with `yet_another_wizz` starting from version 3.1.",
    DeprecationWarning,
    stacklevel=2
)
