"""Synchronous interface for interacting with documents."""

__all__ = ["Documents"]

from typing import Optional

from fixpoint_common.types.documents import (
    Document,
    ListDocumentsResponse,
)
from ._config import Config
from .._common.core import RequestOptions
from .._common.documents import (
    create_document,
    get_document,
    list_documents,
    update_document,
)


class Documents:
    """Synchronous interface for interacting with documents."""

    _config: Config

    def __init__(self, config: Config):
        self._config = config

    def list(
        self,
        path: Optional[str] = None,
        workflow_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        task: Optional[str] = None,
        step: Optional[str] = None,
        opts: Optional[RequestOptions] = None,
    ) -> ListDocumentsResponse:
        """List documents."""
        return list_documents(
            self._config.http_client,
            self._config.core,
            opts or {},
            path=path,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            task=task,
            step=step,
        )

    def get(
        self,
        doc_id: str,
        workflow_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        opts: Optional[RequestOptions] = None,
    ) -> Optional[Document]:
        """Get a document by ID."""
        return get_document(
            self._config.http_client,
            self._config.core,
            opts or {},
            doc_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
        )

    def create(self, doc: Document, opts: Optional[RequestOptions] = None) -> Document:
        """Create a document."""
        return create_document(
            self._config.http_client,
            self._config.core,
            opts or {},
            doc,
        )

    def update(
        self, doc_id: str, doc: Document, opts: Optional[RequestOptions] = None
    ) -> Document:
        """Update a document."""
        return update_document(
            self._config.http_client,
            self._config.core,
            opts or {},
            doc_id,
            doc,
        )
