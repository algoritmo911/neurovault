import os
import json
import csv
import docx
import pypdf
import yaml

from abc import ABC, abstractmethod
from katana.logging_config import get_logger

logger = get_logger(__name__)

class BaseParser(ABC):
    """Abstract base class for file parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        Parses the file and returns its text content.

        :param file_path: Path to the file.
        :return: Extracted text content as a string.
        """
        pass


class TxtParser(BaseParser):
    """Parses plain text files."""

    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


class PdfParser(BaseParser):
    """Parses PDF files."""

    def parse(self, file_path: str) -> str:
        text = []
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)


class DocxParser(BaseParser):
    """Parses DOCX files."""

    def parse(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        text = [p.text for p in doc.paragraphs]
        return "\n".join(text)


class JsonParser(BaseParser):
    """Parses JSON files."""

    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2) # Pretty print for better readability


class YamlParser(BaseParser):
    """Parses YAML files."""

    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # Convert to string, could be YAML or JSON representation
        return yaml.dump(data, default_flow_style=False)


class CsvParser(BaseParser):
    """Parses CSV files."""

    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", newline='') as f:
            reader = csv.reader(f)
            rows = ["\t".join(row) for row in reader]
        return "\n".join(rows)


class ParserFactory:
    """Factory for creating file parsers."""

    def __init__(self):
        self._parsers = {
            ".txt": TxtParser(),
            ".md": TxtParser(),
            ".pdf": PdfParser(),
            ".docx": DocxParser(),
            ".json": JsonParser(),
            ".yaml": YamlParser(),
            ".yml": YamlParser(),
            ".csv": CsvParser(),
        }

    def get_parser(self, file_path: str) -> BaseParser | None:
        """
        Returns a parser for the given file type.

        :param file_path: Path to the file.
        :return: A parser instance or None if the file type is not supported.
        """
        ext = os.path.splitext(file_path)[1].lower()
        return self._parsers.get(ext)


def parse_document(file_path: str) -> str | None:
    """
    High-level function to parse a document.

    :param file_path: Path to the document file.
    :return: The extracted text content, or None if the file type is not supported.
    """
    factory = ParserFactory()
    parser = factory.get_parser(file_path)
    if parser:
        try:
            return parser.parse(file_path)
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None
    else:
        logger.warning(f"Unsupported file type for: {file_path}")
        return None
