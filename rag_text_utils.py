from pathlib import Path
import logging

logger = logging.getLogger("rag_text_utils")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [rag_text_utils] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def process_text_file_for_rag(
    file_path: Path,
    chunk_size: int = 1000,
    overlap: int = 0
) -> list:
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk:
                chunks.append(chunk)
        logger.info(f"Text file processed for RAG: {file_path.name}, chunks: {len(chunks)}")
        return chunks
    except Exception as e:
        logger.error(f"process_text_file_for_rag error: {e}")
        return [f"[Ошибка обработки txt-файла для RAG]: {e}"]
