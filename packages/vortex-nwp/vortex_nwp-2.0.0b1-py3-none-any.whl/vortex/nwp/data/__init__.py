"""
Data resources (mostly NWP).
"""

# Recursive inclusion of packages with potential FootprintBase classes
from . import boundaries, climfiles, consts, diagnostics, executables, fields
from . import assim, gridfiles, logs, modelstates, namelists, obs, surfex, eps, eda
from . import providers, stores, query, monitoring, ctpini
from . import oopsexec, configfiles

#: No automatic export
__all__ = []
