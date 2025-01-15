"""Top-level package for SciDatS."""

__author__ = """mark doerr"""
__email__ = "mark@uni-greifswald.de"
__version__ = "0.0.10"

from .scidats_impl import SciDatS
from .metadata_model_scidats_core import SciDatSMetaDataCore
from .metadata_model_scidats_dcmi import DCMIMetaData

__all__ = ["SciDatS", "SciDatSMetaDataCore"]
