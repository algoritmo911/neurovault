import unittest
import os
from unittest.mock import patch, MagicMock

# Add project root to path to allow absolute imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from katana.parser.factory import ParserFactory, TxtParser, DocxParser, PdfParser, JsonParser, YamlParser, CsvParser, parse_document

# Define the path to the sample files directory
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample_files')


class TestParserFactory(unittest.TestCase):

    def setUp(self):
        self.factory = ParserFactory()

    def test_get_parser(self):
        """Test that the factory returns the correct parser for each file type."""
        self.assertIsInstance(self.factory.get_parser("test.txt"), TxtParser)
        self.assertIsInstance(self.factory.get_parser("test.md"), TxtParser)
        self.assertIsInstance(self.factory.get_parser("test.docx"), DocxParser)
        self.assertIsInstance(self.factory.get_parser("test.pdf"), PdfParser)
        self.assertIsInstance(self.factory.get_parser("test.json"), JsonParser)
        self.assertIsInstance(self.factory.get_parser("test.yaml"), YamlParser)
        self.assertIsInstance(self.factory.get_parser("test.yml"), YamlParser)
        self.assertIsInstance(self.factory.get_parser("test.csv"), CsvParser)
        self.assertIsNone(self.factory.get_parser("test.unsupported"))

    def test_txt_parser(self):
        """Test the TxtParser."""
        parser = TxtParser()
        content = parser.parse(os.path.join(SAMPLES_DIR, 'test.txt'))
        self.assertIn("This is a test text file.", content)
        self.assertIn("The quick brown fox", content)

    def test_json_parser(self):
        """Test the JsonParser."""
        parser = JsonParser()
        content = parser.parse(os.path.join(SAMPLES_DIR, 'test.json'))
        self.assertIn('"name": "Katana AI"', content)
        self.assertIn('"language": "Python"', content)

    def test_yaml_parser(self):
        """Test the YamlParser."""
        parser = YamlParser()
        content = parser.parse(os.path.join(SAMPLES_DIR, 'test.yaml'))
        self.assertIn("name: Katana AI", content)
        self.assertIn("language: Python", content)

    def test_csv_parser(self):
        """Test the CsvParser."""
        parser = CsvParser()
        content = parser.parse(os.path.join(SAMPLES_DIR, 'test.csv'))
        self.assertIn("1\tApple\tFruit", content)
        self.assertIn("3\tKatana\tWeapon", content)

    @patch('docx.Document')
    def test_docx_parser(self, mock_docx):
        """Test the DocxParser using a mock."""
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "This is a docx test."
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "It is mocked."

        mock_document = MagicMock()
        mock_document.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_docx.return_value = mock_document

        parser = DocxParser()
        content = parser.parse("fake_path.docx")

        self.assertEqual("This is a docx test.\nIt is mocked.", content)
        mock_docx.assert_called_once_with("fake_path.docx")

    @patch('pypdf.PdfReader')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_pdf_parser(self, mock_open, mock_pdf_reader):
        """Test the PdfParser using a mock."""
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "This is page 1 of the PDF."
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "This is page 2."

        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        parser = PdfParser()
        content = parser.parse("fake_path.pdf")

        self.assertEqual("This is page 1 of the PDF.\nThis is page 2.", content)
        mock_open.assert_called_once_with("fake_path.pdf", "rb")

    def test_parse_document_unsupported(self):
        """Test the main parse_document function with an unsupported file type."""
        content = parse_document("test.xyz")
        self.assertIsNone(content)

    def test_parse_document_empty_file(self):
        """Test parsing an empty file."""
        # Create an empty file for testing
        empty_file_path = os.path.join(SAMPLES_DIR, 'empty.txt')
        with open(empty_file_path, 'w') as f:
            pass

        content = parse_document(empty_file_path)
        self.assertEqual(content, "")

        # Clean up the empty file
        os.remove(empty_file_path)

if __name__ == '__main__':
    unittest.main()
