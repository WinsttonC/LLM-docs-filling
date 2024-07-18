import os
import re
import warnings

from docx import Document
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from .prompts.schema_prompts import (
    describe_doc_prompt,
    describe_part_prompt,
    generate_doc_title_prompt,
    generate_question_prompt,
)

load_dotenv()


warnings.filterwarnings("ignore")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False)


def generate_questions(entity):
    """
    Используя описание пропуска в документе и
    опц. контекст, в котором пропуск находится
    генерирует ввопрос для уточнения данных
    у пользователя.

    Parameters
    ----------
    entity : str
        Описание пропуска из документа.

    Returns
    ---------
    question : str
        Вопрос пользователю для уточнения
        данных для заполнения пропуска.
    """

    messages = [SystemMessage(content=generate_question_prompt)]
    messages.append(HumanMessage(content=f"Поле: {entity}\n\n Вопрос пользователю:"))
    res = chat(messages)
    question = res.content

    return question


def split_doc(text, words_per_chunk=200):
    """
    Очищает текст от лишних символов и делит его
    на части по n слов.

    Parameters
    ----------
    entity : str
        Текст.

    Returns
    ---------
    chunks : list[str]
        Список из частей документа по n слов.
    """

    cleaned_text = re.sub(r"\[\[.*?\]\]", "", text)
    words = cleaned_text.split(" ")
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
    """
    Генерирует текст с описанием части документа.

    Parameters
    ----------
    text : str
        Часть документа.

    Returns
    ---------
    desc : str
        Описание части документа.
    """

    messages = [SystemMessage(content=describe_part_prompt)]
    messages.append(HumanMessage(content=f"Часть документа:\n {text}"))
    desc = chat(messages)
    desc = desc.content

    return desc


def generate_doc_description(file_path):
    """
    Используя краткое описание частей документа, генерирует
    характеристику документа в 5-6 предложений.

    Parameters
    ----------
    file_path : str
        Путь к документу в формате .docx.

    Returns
    ---------
    desc : str
        Характеристика документа.
    """

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
    """
    Используя характеристику документа, генерирует
    название.

    Parameters
    ----------
    doc_description : str
        Описание документа в виде текста.

    Returns
    ---------
    title : str
        Наиболее подходящее название под
        описание документа.
    """

    messages = [SystemMessage(content=generate_doc_title_prompt)]
    messages.append(
        HumanMessage(content=f"Описание документа:\n {doc_description}\n Название:")
    )
    title = chat(messages)
    title = title.content

    return title
