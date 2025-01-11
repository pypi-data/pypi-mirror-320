######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.13.3                                                                                 #
# Generated on 2025-01-10T15:23:16.016384                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

