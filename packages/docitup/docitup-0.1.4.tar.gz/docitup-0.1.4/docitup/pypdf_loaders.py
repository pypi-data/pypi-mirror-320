from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document as LCDocument
from pypdf import PdfReader
from typing import Iterator, List, Optional, Dict, Any

from .base_loaders import BaseLoader as LCBaseLoader

class PyPdfLoader(BaseLoader, LCBaseLoader):
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
        self.splitter_type = splitter_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.extra_metadata = extra_metadata

    def lazy_load(self) -> Iterator[LCDocument]:
        # List to store split documents
        all_documents: List[LCDocument] = []

        # Process each file path
        for source in self._file_paths:
            pdf_reader = PdfReader(source)  # Correct usage of PdfReader
            page_num = 0

            for page in pdf_reader.pages:  # Iterate over the pages attribute
                # Prepare base metadata
                page_num += 1
                metadata: Dict[str, Any] = {"source": source, "page_number": page_num}

                text = page.extract_text()  # Extract text from each page
                
                # Merge extra_metadata if provided
                if self.extra_metadata:
                    metadata.update(self.extra_metadata)
                
                # Use _text_splitter to break the document into chunks
                chunks = self._text_splitter(
                    splitter_type=self.splitter_type,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    documents=text,  # Pass the combined text
                    metadata=metadata
                )
                
                # Add the chunks to the list
                all_documents.extend(chunks)
        
        # Return the documents as an iterator
        return iter(all_documents)