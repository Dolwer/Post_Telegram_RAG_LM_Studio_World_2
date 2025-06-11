import pandas as pd
from bs4 import BeautifulSoup
import docx
from pathlib import Path
import logging

try:
    import textract
except ImportError:
    textract = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger("rag_file_utils")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [rag_file_utils] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def extract_text_from_file(path: Path) -> str:
    ext = path.suffix.lower()
    try:
        if ext == ".txt":
            logger.info(f"Extracting text from TXT file: {path}")
            return path.read_text(encoding="utf-8", errors='ignore')
        elif ext == ".html":
            logger.info(f"Extracting text from HTML file: {path}")
            html_content = path.read_text(encoding="utf-8", errors='ignore')
            soup = BeautifulSoup(html_content, "html.parser")
            return soup.get_text(separator=" ")
        elif ext in [".csv"]:
            logger.info(f"Extracting text from CSV file: {path}")
            try:
                df = pd.read_csv(path)
                return df.to_csv(sep="\t", index=False)
            except Exception as e:
                logger.error(f"Error reading CSV with pandas: {e}")
                return path.read_text(encoding="utf-8", errors='ignore')
        elif ext in [".xlsx", ".xls", ".xlsm"]:
            logger.info(f"Extracting text from Excel file: {path}")
            try:
                df = pd.read_excel(path)
                return df.to_csv(sep="\t", index=False)
            except Exception as e:
                logger.error(f"Error reading Excel with pandas: {e}")
                return ''
        elif ext in [".docx"]:
            logger.info(f"Extracting text from DOCX file: {path}")
            try:
                doc = docx.Document(path)
                return "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                logger.error(f"Error reading DOCX: {e}")
                return ''
        elif ext in [".doc"]:
            logger.info(f"Extracting text from DOC file: {path}")
            if textract is not None:
                try:
                    return textract.process(str(path)).decode("utf-8")
                except Exception as e:
                    logger.error(f"Error extracting DOC with textract: {e}")
                    return ''
            else:
                logger.error("textract is not installed. Cannot parse DOC files.")
                return ''
        elif ext == ".pdf":
            logger.info(f"Extracting text from PDF file: {path}")
            if PyPDF2 is not None:
                try:
                    text = []
                    with open(path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text.append(page_text)
                    return "\n".join(text)
                except Exception as e:
                    logger.error(f"Error extracting PDF with PyPDF2: {e}")
                    return ''
            elif textract is not None:
                try:
                    return textract.process(str(path)).decode("utf-8")
                except Exception as e:
                    logger.error(f"Error extracting PDF with textract: {e}")
                    return ''
            else:
                logger.error("Neither PyPDF2 nor textract installed. Cannot parse PDF files.")
                return ''
        else:
            logger.warning(f"Unsupported file type: {path}")
            return ''
    except Exception as e:
        logger.error(f"Exception extracting text from {path}: {e}")
        return ''

def clean_html_from_cell(cell_value) -> str:
    if isinstance(cell_value, str):
        return BeautifulSoup(cell_value, "html.parser").get_text(separator=" ")
    return str(cell_value)
