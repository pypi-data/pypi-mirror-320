"""Error and exception definitions for structured workflows."""

__all__ = [
    "StructuredException",
    "DefinitionError",
    "InternalError",
]

from fixpoint_common.errors import FixpointError


class StructuredException(FixpointError):
    """The base class for all structured workflow exceptions."""


class DefinitionError(StructuredException):
    """Raised when there is an error in the definition of a structured workflow

    The DefinitionException is raised when defining an invalid structured
    workflow, task, or step. It can also be raised when we begin executing an
    ill-defined workflow, task, or step. It does not mean that computation
    raised an exception, but rather that the structure of your workflow program
    is wrong.
    """


class InternalError(StructuredException):
    """An internal error (non-user) in the structured workflows library"""
