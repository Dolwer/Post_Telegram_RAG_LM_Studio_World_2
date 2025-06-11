from pathlib import Path
import logging

logger = logging.getLogger("rag_prompt_utils")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [rag_prompt_utils] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def get_prompt_parts(
    data_dir: Path,
    topic: str,
    context: str,
    uploadfile=None,
    file1=None,
    file2=None
) -> str:
    import random

    def read_template(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading prompt template {path}: {e}")
            return None

    prompt1_dir = Path(data_dir) / "prompt_1"
    prompt2_dir = Path(data_dir) / "prompt_2"
    template = None

    if file1 is not None and file2 is not None:
        logger.info(f"Deterministic prompt: {file1.name} + {file2.name}")
        txt1 = read_template(file1)
        txt2 = read_template(file2)
        if txt1 is not None and txt2 is not None:
            template = txt1 + "\n" + txt2
    elif prompt1_dir.exists() and prompt2_dir.exists():
        prompt1_files = list(prompt1_dir.glob("*.txt"))
        prompt2_files = list(prompt2_dir.glob("*.txt"))
        if prompt1_files and prompt2_files:
            f1 = random.choice(prompt1_files)
            f2 = random.choice(prompt2_files)
            logger.info(f"Random prompt: {f1.name} + {f2.name}")
            txt1 = read_template(f1)
            txt2 = read_template(f2)
            if txt1 is not None and txt2 is not None:
                template = txt1 + "\n" + txt2
    if template is None:
        prompt_file = Path(data_dir) / "prompt.txt"
        if prompt_file.exists():
            logger.warning("Fallback to prompt.txt")
            template = read_template(prompt_file)
        else:
            logger.warning("Fallback to plain topic + context")
            return f"{topic}\n\n{context}"

    if template is None:
        return f"{topic}\n\n{context}"

    has_uploadfile = "{UPLOADFILE}" in template

    uploadfile_text = ""
    if has_uploadfile:
        if uploadfile is not None:
            try:
                file_path = Path(uploadfile)
                if file_path.exists():
                    uploadfile_text = file_path.name
                    context = context[:1024]
                else:
                    uploadfile_text = f"[Файл не найден: {file_path.name}]"
            except Exception as e:
                uploadfile_text = "[Ошибка с файлом]"
                logger.error(f"Error processing uploadfile: {e}")
        else:
            uploadfile_text = "[Файл не передан]"

    if not has_uploadfile:
        context = context[:4096]

    prompt_out = (
        template.replace("{TOPIC}", topic)
                .replace("{CONTEXT}", context)
    )
    if has_uploadfile:
        prompt_out = prompt_out.replace("{UPLOADFILE}", uploadfile_text)
    return prompt_out
