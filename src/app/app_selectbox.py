import os
import asyncio

import aiohttp
import pandas as pd
import requests
import streamlit as st
from config import description
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from chat import chat
from input_processing import extract_doc, clarify_question, approve_user_question, find_documents
load_dotenv()

APP_URL = os.getenv("APP_URL")

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
        
        if st.session_state.conversation_status == 'base':
            input_status = approve_user_question(prompt)
            print('input_status')
            print(input_status)
            if input_status == 'да':

                st.session_state.conversation_status = 'show_docs'
                
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
                
        if st.session_state.conversation_status == 'clarify_question':
            previous_prompt = st.session_state.previous_prompt
            prompt = f'Вопрос: {previous_prompt}\nУточнение:\n{prompt}'
            st.session_state.conversation_status = 'base'  
        
        if st.session_state.conversation_status == 'show_docs':
            doc_name = extract_doc(prompt)
            relevant_docs = find_documents(doc_name)
            st.session_state.relevant_docs = relevant_docs.append('Нужного документа нет в списке')
            with st.chat_message("assistant"):
                str_docs = ', '.join(relevant_docs) # TODO: с маленькой буквы или написать по другому
                answer = f'Были найдены следующие релевантные документы:\n{str_docs}\n\nВыберите из них тот, что вам нужен.'
                st.write(answer)
            st.session_state.messages.append({"role": "assistant", 
                                "content": AIMessage(content=answer)})
            st.session_state.conversation_status = 'choose_doc'
        
        if st.session_state.conversation_status == 'choose_doc':
            
            with st.chat_message("assistant"):
                selected_doc = st.selectbox('Выберите документ', st.session_state.relevant_docs, index=None)
                st.write(f'Вы выбрали: {selected_doc}.')
                fill_doc = st.button("Заполнить документ")
                if fill_doc:
                    st.session_state.step = 3
        

    if st.sidebar.button("Вернуться к описанию"):
        st.session_state.step = 1
        st.rerun()


elif st.session_state.step == 3:
    st.header('Заполнение документов')
    return_to_chat = st.button('Вернуться в чат')
    if return_to_chat:
        st.session_state.step = 2