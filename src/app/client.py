import os
import asyncio

import aiohttp
import pandas as pd
import requests
import streamlit as st
from config import description
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import json
from utils import check_schema_existance
from schema import create_schema
from fill_fields_rules import fill_fields_rules
from fill_fields_LLM import fill_fields_LLM
from chat import chat
from input_processing import extract_doc, clarify_question, approve_user_question, find_documents
load_dotenv()

APP_URL = os.getenv("APP_URL")
doc_path = os.getenv("DOCUMENTS_PATH")

# ===============================================================
# СТРАНИЦЫ

# ===============================================================

chat_prompt = 'Отвечай на вопросы пользователя'
if "step" not in st.session_state:
    st.session_state.step = 1
if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'assistant',
                                  'content': SystemMessage(content=chat_prompt)}]
if "conversation_status" not in st.session_state:
    st.session_state.conversation_status = 'base'
if "previous_prompt" not in st.session_state:
    st.session_state.previous_prompt = ''
if 'selected_doc' not in st.session_state:
    st.session_state.selected_doc = None
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# if "model" not in st.session_state:
#     st.session_state.model = None
def fill_docs():
    st.session_state.selected_doc = selected_doc
    st.session_state.messages.append({"role": "assistant", 
                                "content": AIMessage(content=f'Вы выбрали: {selected_doc}')})

if st.session_state.step == 1:
    st.title("Заполнение документов с GigaChat")
    st.header("")

    # ============= ВСТАВИТЬ ОПИСАНИЕ РЕШЕНИЯ ==================

    if st.button("Заполнить свой документ"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.header("Заполнение документов")
    st.markdown("""
                Чтобы заполнить документ, напишите в чат.
                Если документа нет в базе, его можно добавить, используя 
                кнопку ниже.
                """)


    for message in st.session_state.messages[1:]:
        with st.chat_message(message['role']):
            st.markdown(message['content'].content)

    if prompt := st.chat_input("Что нужно сделать"):

        print(f'=== ПРОМПТ ===\n{prompt}')
        st.session_state.messages.append({'role': 'user',
                                          'content': HumanMessage(content=prompt)})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        if st.session_state.conversation_status == 'clarify_question':
            previous_prompt = st.session_state.previous_prompt
            prompt = f'Вопрос: {previous_prompt}\nУточнение:\n{prompt}'
            st.session_state.conversation_status = 'base'

        input_status = approve_user_question(prompt)
        if input_status == 'да':
            doc_name = extract_doc(prompt)
            relevant_docs = find_documents(doc_name)
            selected_doc = relevant_docs[0]
            st.session_state.selected_doc = relevant_docs[0]
            if not check_schema_existance(selected_doc):  # TODO:
                create_schema(selected_doc)
            st.session_state.step = 3
            st.rerun()

        else:
            st.session_state.conversation_status = 'clarify_question'
            with st.chat_message("assistant"):
                q = clarify_question(prompt)
                st.session_state.previous_prompt = prompt
                st.session_state.conversation_status = 'clarify_question'
                print('q')
                print(q)
                st.write(q)
            st.session_state.messages.append({"role": "assistant", 
                                            "content": AIMessage(content=q)})
            
    if st.sidebar.button("Вернуться к описанию"):
        st.session_state.step = 1
        st.rerun()


elif st.session_state.step == 3:
    selected_doc = st.session_state.selected_doc
    with open(f'{doc_path}/doc_schemas/{selected_doc}.json', 'r', encoding='utf-8') as f:
        schema = json.load(f)

    st.header('Заполнение документа')
    st.markdown(f"""
                #### Выбран документ: {st.session_state.selected_doc}
                **Описание**:\n
                {schema['description']} \n\n
                **В документе нужно заполнить следующие поля:**
                """)

    st.session_state.form_data = {}

    with st.form("my_form"):
        fields = schema['fields']

        field_names = [field for field in fields]
        questions = [fields[field]['question'] for field in fields]

        for i in range(len(field_names)):
            
            a = st.text_input(questions[i], key=f'text_input_{i}')
            st.write('\n')
            # st.write(f'{fields[i]}: {a}')
            # value = st.text_input(f'Текст {elem}', key=f'text_input_{elem}')
            # # Сохранение значений в словаре session_state

            
            st.session_state.form_data[field_names[i]] = a


        submitted = st.form_submit_button("Заполнить")
        if submitted:
            st.write("Введенные данные:")
            st.write(st.session_state.form_data)
            form_data = st.session_state.form_data
            
            # with open('schema.json', 'r', encoding='utf-8') as f:
            #     schema = json.load(f)
            
            # for key in form_data:
            #     user_answer = form_data[key]
            #     schema[key]['user_answer'] = user_answer
            
            # with open('schema.json', 'w', encoding='utf-8') as f:
            #     json.dump(schema, f, ensure_ascii=False, indent=4)
            
            # fill_fields_rules(selected_doc, form_data)
            with st.spinner('Заполняю документ. Пожалуйста, подождите.'):
                fill_fields_LLM(selected_doc, form_data)
            
            # Создайте кнопку для загрузки
    file_path = f'{doc_path}/user_docs/{selected_doc}.docx'
    with open(file_path, "rb") as file:
        file_data = file.read()
    
    # Установите имя файла для загрузки
    file_name = os.path.basename(file_path)
    st.download_button(
        label="Скачать файл",
        data=file_data,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
            # st.session_state.step = 1
            # st.rerun()


    return_to_chat = st.button('Вернуться в чат')
    if return_to_chat:
        st.session_state.step = 2