import pdfplumber
from typing import Dict, List, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PdfExtractor:
    """Extract text, tables, and metadata from PDF files."""

    def __init__(self, pdf_path: str):
        """
        Initialize PDF extractor.

        Args:
            pdf_path: Path to the PDF file to extract from
        """
        self.pdf_path = Path(pdf_path)
        self.document_name = self.pdf_path.stem

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not self.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")

    def extract_all(self) -> Dict:
        """
        Extract all content from PDF.

        Returns:
            Dictionary containing metadata, text, tables, and page count
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                logger.info(f"Extracting from {self.document_name} ({len(pdf.pages)} pages)")

                return {
                    'metadata': self.extract_metadata(pdf),
                    'text': self.extract_text(pdf),
                    'tables': self.extract_tables(pdf),
                    'page_count': len(pdf.pages),
                    'document_name': self.document_name
                }
        except Exception as e:
            logger.error(f"Error extracting PDF {self.pdf_path}: {str(e)}")
            raise

    def extract_text(self, pdf) -> List[Dict]:
        """
        Extract text from each page.

        Args:
            pdf: pdfplumber PDF object

        Returns:
            List of dictionaries with page_number and text
        """
        pages = []
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        'page_number': i + 1,
                        'text': text.strip()
                    })
                    logger.debug(f"Extracted {len(text)} characters from page {i + 1}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {i + 1}: {str(e)}")
                continue

        return pages

    def extract_tables(self, pdf) -> List[Dict]:
        """
        Extract tables from PDF (common in spec sheets).

        Args:
            pdf: pdfplumber PDF object

        Returns:
            List of dictionaries with page_number and table data
        """
        tables = []
        for i, page in enumerate(pdf.pages):
            try:
                page_tables = page.extract_tables()
                if page_tables:
                    for table_idx, table in enumerate(page_tables):
                        # Filter out empty tables
                        if table and len(table) > 0:
                            # Clean up table data - remove None values
                            cleaned_table = [
                                [cell.strip() if cell else '' for cell in row]
                                for row in table
                            ]

                            tables.append({
                                'page_number': i + 1,
                                'table_number': table_idx + 1,
                                'data': cleaned_table,
                                'rows': len(cleaned_table),
                                'columns': len(cleaned_table[0]) if cleaned_table else 0
                            })
                            logger.debug(f"Extracted table {table_idx + 1} from page {i + 1}")
            except Exception as e:
                logger.warning(f"Error extracting tables from page {i + 1}: {str(e)}")
                continue

        return tables

    def extract_metadata(self, pdf) -> Dict:
        """
        Extract PDF metadata.

        Args:
            pdf: pdfplumber PDF object

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            metadata = pdf.metadata or {}
            return {
                'title': metadata.get('Title', ''),
                'author': metadata.get('Author', ''),
                'subject': metadata.get('Subject', ''),
                'creator': metadata.get('Creator', ''),
                'producer': metadata.get('Producer', ''),
                'creation_date': str(metadata.get('CreationDate', '')),
            }
        except Exception as e:
            logger.warning(f"Error extracting metadata: {str(e)}")
            return {}

    def extract_page(self, page_number: int) -> Optional[Dict]:
        """
        Extract content from a specific page.

        Args:
            page_number: Page number to extract (1-indexed)

        Returns:
            Dictionary with text and tables from the specified page
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    raise ValueError(f"Page number {page_number} out of range (1-{len(pdf.pages)})")

                page = pdf.pages[page_number - 1]
                text = page.extract_text()
                tables = page.extract_tables()

                return {
                    'page_number': page_number,
                    'text': text.strip() if text else '',
                    'tables': tables if tables else [],
                    'has_images': len(page.images) > 0,
                    'image_count': len(page.images)
                }
        except Exception as e:
            logger.error(f"Error extracting page {page_number}: {str(e)}")
            return None

    def get_page_count(self) -> int:
        """
        Get the total number of pages in the PDF.

        Returns:
            Number of pages
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            return 0

    def extract_text_only(self) -> str:
        """
        Extract all text from PDF as a single string.

        Returns:
            Complete text from all pages
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                all_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                return '\n\n'.join(all_text)
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ''
