import json
import os
import re
from datetime import datetime

from .agents.schema_processing_agents import (
    generate_doc_description,
    generate_doc_title,
    generate_questions,
)
from docx import Document
from dotenv import load_dotenv
from .chroma import add_documents_to_vectorstore

load_dotenv()

doc_path = os.getenv("DOCUMENTS_PATH")


def check_doc_existance(doc_name):
    file_path = f"{doc_path}/documents/{doc_name}.docx"
    if os.path.exists(file_path):
        return True
    else:
        return False


def check_schema_existance(doc_name):
    file_path = f"{doc_path}/doc_schemas/{doc_name}.json"
    # file_path = f'doc_schemas/{doc_name}'
    if os.path.exists(file_path):
        return True
    else:
        return False


def extract_entities_with_context(text, n=13):
    pattern = r"\[\[(.*?)\]\]"
    matches = re.finditer(pattern, text)
    words = text.split()

    entities_with_context = {}

    for match in matches:
        entity = match.group(1)
        start, end = match.span()

        # Найти индекс начала и конца сущности в списке слов
        start_idx = len(re.findall(r"\S+", text[:start]))
        end_idx = start_idx + len(re.findall(r"\S+", entity))

        # Получить контекстные слова
        context_start_idx = max(0, start_idx - n)
        context_end_idx = min(len(words), end_idx + n)

        context_before = " ".join(words[context_start_idx:start_idx])
        context_after = " ".join(words[end_idx:context_end_idx])
        context = f"{context_before} _____________ {context_after}"

        entities_with_context[entity] = {
            "context": context,
        }

    return entities_with_context


def create_schema(doc_name: str, new_doc=False):
    file_path = f"{doc_path}/documents/{doc_name}.docx"

    print(f"=== СОЗДАНИЕ ШАБЛОНА ДЛЯ ДОКУМЕНТА {doc_name} ===")

    doc_with_entities = Document(file_path)

    text_with_entities = [p.text for p in doc_with_entities.paragraphs]
    text_with_entities = "\n".join(text_with_entities)

    entities_dict = extract_entities_with_context(text_with_entities)

    for entity in entities_dict:
        entities_dict[entity]["question"] = generate_questions(entity)

    fill_dict = {}
    current_datetime = datetime.now()

    fill_dict["description"] = generate_doc_description(file_path)

    fill_dict["fields"] = entities_dict
    fill_dict["last_update"] = current_datetime.strftime("%Y-%m-%d")
    fill_dict["title"] = generate_doc_title(fill_dict["description"])

    if new_doc:
        # Замена названия в загруженном документе на сгенерированное

        new_doc_name = fill_dict["title"]
        new_doc_name = re.sub(r'[\\/*?:"<>|]', "", new_doc_name)
        new_file_path = f"{doc_path}/documents/{new_doc_name}.docx"

        os.rename(file_path, new_file_path)

        new_doc_name = fill_dict["title"]
        add_documents_to_vectorstore(new_doc_name)
        path = f"{doc_path}/doc_schemas/{new_doc_name}.json"

    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(fill_dict, json_file, indent=4)
