import os
import warnings

from docx import Document
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from prompts import generate_question_prompt, generate_doc_title_prompt, describe_part_prompt, describe_doc_prompt

load_dotenv()
import re



warnings.filterwarnings("ignore")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False)


def generate_questions(entity):
    messages = [SystemMessage(content=generate_question_prompt)]
    messages.append(HumanMessage(content=f"Поле: {entity}\n\n Вопрос пользователю:"))
    res = chat(messages)
    question = res.content

    return question


def split_doc(text, words_per_chunk=200):
    cleaned_text = re.sub(r"\[\[.*?\]\]", "", text)
    words = cleaned_text.split(" ")  # re.findall(r'\b\w+\b', text)
    chunks = []
    current_chunk = []
    word_count = 0

    for word in words:
        current_chunk.append(word)
        word_count += 1

        if word_count == words_per_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            word_count = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def generate_part_description(text):
    messages = [SystemMessage(content=describe_part_prompt)]
    messages.append(HumanMessage(content=f"Часть документа:\n {text}"))
    desc = chat(messages)
    desc = desc.content

    return desc


def generate_doc_description(file_path):
    doc_with_entities = Document(file_path)

    text = [p.text for p in doc_with_entities.paragraphs]
    text = "\n".join(text)

    chunks = split_doc(text)
    chunk_descriptions = [generate_part_description(chunk) for chunk in chunks]
    chunk_descriptions = "\n".join(chunk_descriptions)
    messages = [SystemMessage(content=describe_doc_prompt)]
    messages.append(
        HumanMessage(
            content=f"Краткое содержание частей документа:\n {chunk_descriptions}"
        )
    )
    desc = chat(messages)
    desc = desc.content

    return desc


def generate_doc_title(doc_description):
    messages = [SystemMessage(content=generate_doc_title_prompt)]
    messages.append(
        HumanMessage(content=f"Описание документа:\n {doc_description}\n Название:")
    )
    title = chat(messages)
    title = title.content

    return title
