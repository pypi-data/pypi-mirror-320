"""Module for common code among resource identifiers."""

__all__ = [
    "new_human_task_entry_id",
    "new_research_record_id",
    "new_research_document_id",
    "new_workflow_id",
    "new_workflow_run_id",
    "new_workflow_run_attempt_id",
    "new_crawl_parse_job_id",
    "new_agent_id",
    "new_agent_memory_item_id",
    "new_job_id",
    "new_task_id",
]

from typing import Optional
import uuid


def new_human_task_entry_id() -> str:
    """Create a new workflow run id"""
    return _make_resource_uuid("ht")


def new_research_record_id() -> str:
    """Create a new research record id"""
    return _make_resource_uuid("rrec")


def new_research_document_id() -> str:
    """Create a new research document id"""
    return _make_resource_uuid("rdoc")


def new_workflow_id() -> str:
    """Create a new workflow id"""
    return _make_resource_uuid("wf")


def new_workflow_run_id() -> str:
    """Create a new workflow run id"""
    return _make_resource_uuid("wfrun")


def new_workflow_run_attempt_id() -> str:
    """Create a new workflow run id"""
    return _make_resource_uuid("wfrunatmpt")


def new_crawl_parse_job_id(suffix: Optional[str] = None) -> str:
    """Create a new crawl parse job id"""
    prefix = "crawlparse"
    if suffix is None:
        return _make_resource_uuid(prefix)
    return _make_resource(prefix, suffix)


def new_agent_id() -> str:
    """Generate a random agent ID if not explicitly given"""
    return _make_resource_uuid("agent")


def new_agent_memory_item_id() -> str:
    """Generate a new agent memory item ID"""
    return _make_resource_uuid("amem")


def _make_resource_uuid(resource_acronym: str) -> str:
    return _make_resource(resource_acronym, str(uuid.uuid4()))


def _make_resource(resource_acronym: str, suffix: str) -> str:
    return "".join([resource_acronym, "-", suffix])


def new_job_id() -> str:
    """Generate a new job ID."""
    return f"job-{str(uuid.uuid4())}"


def new_task_id() -> str:
    """Generate a new task ID (aka a task in a multi-task job)."""
    return f"task-{str(uuid.uuid4())}"
