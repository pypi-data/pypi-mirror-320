from markitdown import MarkItDown # type: ignore
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument
from typing import Iterator, List, Optional, Dict, Any

from .base_loaders import BaseLoader as LCBaseLoader

class MarkitdownLoader(BaseLoader, LCBaseLoader):
    def __init__(
            self, 
            file_path: str | list[str],
            splitter_type: Optional[str] = "recursive", 
            chunk_size: Optional[int] = 1000,
            chunk_overlap: Optional[int] = 100,
            extra_metadata: Optional[Dict[str, Any]] = None
        ) -> None:
        super().__init__()
        self._file_paths = file_path if isinstance(file_path, list) else [file_path]
        self.markitdown = MarkItDown()
        self.splitter_type = splitter_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.extra_metadata = extra_metadata

    def lazy_load(self) -> Iterator[LCDocument]:
        # List to store split documents
        all_documents: List[LCDocument] = []

        # Process each file path
        for source in self._file_paths:
            dl_doc = self.markitdown.convert(source)

            # Prepare base metadata
            metadata = {"source": source}
            
            # Merge extra_metadata if provided
            if self.extra_metadata:
                metadata.update(self.extra_metadata)
            
            # Use _text_splitter to break the document into chunks
            chunks = self._text_splitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                documents=dl_doc.text_content,
                metadata=metadata
            )
            
            # Add the chunks to the list
            all_documents.extend(chunks)
        
        # Return the documents as an iterator
        return iter(all_documents)