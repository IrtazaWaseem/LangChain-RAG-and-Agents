import os
import shutil
import logging
import pytesseract
import platform
from dotenv import load_dotenv
from langchain_unstructured import UnstructuredLoader
from langchain_core.documents import Document
from typing import Iterator
from unstructured.cleaners.core import (
    clean_extra_whitespace,
    clean_dashes,
    clean_bullets,
    clean_trailing_punctuation
)

load_dotenv()
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, mode: str = "fast"):
        self.mode = mode
        self._configure_ocr_paths()

    @staticmethod
    def _configure_ocr_paths():
        tesseract_exe = os.getenv("TESSERACT_PATH")
        poppler_bin = os.getenv("POPPLER_PATH")

        if platform.system() == "Windows":
            if tesseract_exe:
                t_cmd = str(tesseract_exe)
                pytesseract.pytesseract.tesseract_cmd = t_cmd
                t_dir = os.path.dirname(t_cmd)
                if t_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] += os.pathsep + t_dir

            if poppler_bin:
                p_bin = str(poppler_bin)
                if p_bin not in os.environ.get("PATH", ""):
                    os.environ["PATH"] += os.pathsep + p_bin

        has_env = tesseract_exe and os.path.exists(str(tesseract_exe))
        has_global = bool(shutil.which("tesseract"))

        if not (has_env or has_global):
            logger.warning("Tesseract not found. OCR may fail.")

    def load_file(self, file_path: str) -> Iterator[Document]:
        try:
            loader = UnstructuredLoader(file_path=file_path, strategy=self.mode)
            for data in loader.lazy_load():
                yield self._clean_document(data)
        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {str(e)}")
            raise

    @staticmethod
    def _clean_document(doc: Document) -> Document:
        text = doc.page_content
        text = clean_extra_whitespace(text)
        text = clean_dashes(text)
        text = clean_bullets(text)
        text = clean_trailing_punctuation(text)
        doc.page_content = text
        return doc