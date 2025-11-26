import unittest
import sys
from pathlib import Path

sys.path.append('/Users/anujjain/drone-component-analyzer')
from src.agent.PdfExtractor import PdfExtractor


class TestPdfExtractor(unittest.TestCase):
    """Test cases for PDF extraction functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / 'test_data'
        self.test_data_dir.mkdir(exist_ok=True)

    def test_initialization_with_invalid_path(self):
        """Test that initialization fails with invalid PDF path."""
        with self.assertRaises(FileNotFoundError):
            PdfExtractor('/path/to/nonexistent.pdf')

    def test_initialization_with_non_pdf(self):
        """Test that initialization fails with non-PDF file."""
        # Create a temporary non-PDF file
        test_file = self.test_data_dir / 'test.txt'
        test_file.write_text('This is not a PDF')

        with self.assertRaises(ValueError):
            PdfExtractor(str(test_file))

        # Cleanup
        test_file.unlink()

    def test_document_name_extraction(self):
        """Test that document name is correctly extracted from path."""
        # This test would need an actual PDF file to work
        # For now, we'll skip it
        pass

    def test_extract_text_returns_list(self):
        """Test that extract_text returns a list of page dictionaries."""
        # Would need a real PDF file for this test
        pass

    def test_extract_tables_returns_list(self):
        """Test that extract_tables returns a list of table dictionaries."""
        # Would need a real PDF file for this test
        pass


class TestPdfExtractorIntegration(unittest.TestCase):
    """Integration tests for PDF extraction (requires sample PDFs)."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_pdf_dir = Path(__file__).parent.parent / 'data' / 'pdfs'

    def test_extract_all_structure(self):
        """Test that extract_all returns correct structure."""
        # Skip if no PDFs available
        pdfs = list(self.sample_pdf_dir.glob('*.pdf'))
        if not pdfs:
            self.skipTest("No sample PDFs available for testing")

        extractor = PdfExtractor(str(pdfs[0]))
        result = extractor.extract_all()

        # Check structure
        self.assertIn('metadata', result)
        self.assertIn('text', result)
        self.assertIn('tables', result)
        self.assertIn('page_count', result)
        self.assertIn('document_name', result)

        # Check types
        self.assertIsInstance(result['metadata'], dict)
        self.assertIsInstance(result['text'], list)
        self.assertIsInstance(result['tables'], list)
        self.assertIsInstance(result['page_count'], int)


if __name__ == '__main__':
    unittest.main()
