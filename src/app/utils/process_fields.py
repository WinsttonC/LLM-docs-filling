import os
import re

from .agents.find_fields_agent import find_fields
from docx import Document
from dotenv import load_dotenv

load_dotenv()


doc_path = os.getenv("DOCUMENTS_PATH")
BATCH_SIZE = 2


def is_valid_string(input_string):
    pattern = r"^[_. ]+$"
    return not bool(re.match(pattern, input_string))


def shorten_blanks(input_string):
    # Паттерн для поиска длинных пропусков

    if is_valid_string(input_string):
        pattern = r"(_{2,})"
        # Заменяем длинные пропуски на сокращенный вариант
        output_string = re.sub(pattern, "____________", input_string)

        return output_string
    else:
        return ""


def create_fields_template(doc_name, new_doc=False):
    if new_doc:
        file_path = f"{doc_path}/raw_docs/{doc_name}.docx"
    else:
        file_path = f"{doc_path}/documents/{doc_name}.docx"

    doc = Document(file_path)

    final_text = []
    paragraphs = [shorten_blanks(p.text) for p in doc.paragraphs]
    pattern = r"_{2,}"

    length = len(paragraphs)
    for i in range(0, length, BATCH_SIZE):
        batch = paragraphs[i : min(i + BATCH_SIZE, length)]
        input_text = "\n".join(batch)
        match = re.search(pattern, input_text)
        if match:
            input_text = f"Строка:\n {input_text}\nОтвет:"

            content = find_fields(input_text)

            final_text.append(content)
        else:
            final_text.append(input_text)

    save_path = f"{doc_path}/documents/{doc_name}.docx"
    new_doc = Document()

    for text_block in final_text:
        new_doc.add_paragraph(text_block)

    new_doc.save(save_path)
