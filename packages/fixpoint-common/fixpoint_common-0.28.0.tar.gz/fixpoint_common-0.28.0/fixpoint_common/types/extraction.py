"""Types for extraction requests and responses."""

__all__ = [
    "BatchExtractionJob",
    "BatchExtractionJobStatus",
    "BatchExtractionRequestItem",
    "CreateBatchExtractionJobRequest",
    "CreateRecordExtractionRequest",
    "MAX_BATCH_EXTRACTION_REQUESTS",
    "RecordExtraction",
]

from typing import Optional, Union, List
from pydantic import BaseModel, Field

from fixpoint_common.completions import ChatCompletionMessageParam
from fixpoint_common.types.json_extraction import (
    JsonSchemaExtraction,
)
from fixpoint_common.types.metadata import Metadata
from .citations import Citation
from .research import ResearchRecord
from .sources import TextSource, WebpageSource, CrawlUrlSource, BatchTextSource
from .workflow import WorkflowRunId


class CreateRecordExtractionRequest(BaseModel):
    """Request to create Record Q&A extraction."""

    document_id: Optional[str] = None
    document_name: Optional[str] = None
    run_id: Optional[WorkflowRunId] = None

    source: Union[
        CrawlUrlSource,
        WebpageSource,
        TextSource,
        BatchTextSource,
    ] = Field(description="The source of the data to extract.")

    extra_instructions: Optional[List[ChatCompletionMessageParam]] = Field(
        description="Additional prompt instructions",
        default=None,
    )

    questions: List[str] = Field(description="The questions to answer.")

    metadata: Optional[Metadata] = Field(
        default=None, description="Metadata to record for extraction"
    )

    def clone(self) -> "CreateRecordExtractionRequest":
        """Clone the request."""
        return CreateRecordExtractionRequest(**self.model_dump())


class RecordExtraction(BaseModel):
    """Extraction result from a question and answer record extraction."""

    result_record: ResearchRecord = Field(
        description="The research record containing the extracted data."
    )
    citations: List[Citation] = Field(
        description="The citations for the extraction result."
    )
    sub_json_extractions: List[JsonSchemaExtraction] = Field(
        description="The sub-extractions that resulted in this extraction."
    )


MAX_BATCH_EXTRACTION_REQUESTS = 100


class BatchExtractionRequestItem(BaseModel):
    """An inner extraction request within a batch extraction job."""

    run_id: Optional[WorkflowRunId] = Field(
        description=(
            "The run_id is for idempotency. If not set, we will use the outer "
            "request's `job_id`."
        ),
        default=None,
    )

    source: Union[
        CrawlUrlSource,
        WebpageSource,
        TextSource,
        BatchTextSource,
    ] = Field(description="The source of the data to extract.")

    extra_instructions: Optional[List[ChatCompletionMessageParam]] = Field(
        description=(
            "Optional prompt instructions for a single extraction request. "
            "Overrides instructions in the batch job."
        ),
        default=None,
    )

    questions: Optional[List[str]] = Field(
        description=(
            "Questions to answer for a single extraction request. Overrides "
            "questions in the batch job."
        ),
        default=None,
    )

    metadata: Optional[Metadata] = Field(
        description=(
            "Metadata to record for extraction. Overrides the batch metadata."
        ),
        default=None,
    )


class CreateBatchExtractionJobRequest(BaseModel):
    """A request to create a batch record extraction job.

    If you do not specify `questions` in the top-level request, you must set
    them on every item of `requests`.
    """

    document_id: Optional[str] = Field(
        description=(
            "The document id to use for all extractions, unless one of the `requests` "
            "has its own `document_id`."
        ),
        default=None,
    )
    document_name: Optional[str] = Field(
        description=(
            "The document display name to use for all extractions, unless one of the "
            "`requests` has its own `document_name`."
        ),
        default=None,
    )

    job_id: Optional[str] = Field(
        description=(
            "Specify a job_id for idempotency. Otherwise, one will be generated for you."
        ),
        default=None,
    )

    requests: List[BatchExtractionRequestItem] = Field(
        description=(
            "The individual extractions to run in the job."
            f" Max is {MAX_BATCH_EXTRACTION_REQUESTS}."
        ),
        min_length=1,
        max_length=MAX_BATCH_EXTRACTION_REQUESTS,
    )

    questions: Optional[List[str]] = Field(
        description=(
            "The questions to answer/extract per source. If one of the `requests`"
            " specifies `questions`, those are used instead for that request."
        ),
        default=None,
    )

    extra_instructions: Optional[List[ChatCompletionMessageParam]] = Field(
        description=(
            "Additional prompt instructions. If one of the `requests` specifies "
            "`extra_instructions`, those are used instead for that request."
        ),
        default=None,
    )

    metadata: Optional[Metadata] = Field(
        default=None,
        description=(
            "Metadata for document. If one of the `requests` specifies `metadata`,"
            " those are used instead for that request."
        ),
    )


class BatchExtractionJob(BaseModel):
    """A response to a create batch extract job request."""

    job_id: str


class BatchExtractionJobStatus(BaseModel):
    """A response to a get batch extraction job status request."""

    job_id: str
    completed: int
    failed: int
    pending: int
