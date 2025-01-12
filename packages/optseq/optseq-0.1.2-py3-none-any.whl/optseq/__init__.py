from importlib.metadata import metadata

from .optseq import Activity, Mode, Model, Parameters, Resource, State, Temporal

__all__ = ["Activity", "Mode", "Model", "Parameters", "Resource", "State", "Temporal"]

_package_metadata = metadata(str(__package__))
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")
