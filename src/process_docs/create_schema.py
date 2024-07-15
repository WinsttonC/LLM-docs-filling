from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from prompts import question_prompt
from docx import Document
import json
from dotenv import load_dotenv
import os
import re
import warnings
load_dotenv()

warnings.filterwarnings("ignore")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")
BATCH_SIZE = 4

chat = GigaChat(credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False) #model='GigaChat-Pro'
doc_with_entities = Document('processed_arenda.docx')

text_with_entities = [p.text for p in doc_with_entities.paragraphs]
text_with_entities = '\n'.join(text_with_entities)

pattern = r'\[\[(.*?)\]\]'

matches = re.findall(pattern, text_with_entities)

print('======== НАЧАЛО ОБРАБОТКИ ДОКУМЕНТА ========')
print(f'В документе найдено {len(set(matches))} пропусков.')
fill_dict = {}
i = 0
for entity in matches:
    messages = [SystemMessage(content=question_prompt)]
    messages.append(HumanMessage(content=f"Поле: {entity}\n Вопрос пользователю:"))
    res = chat(messages)
    fill_dict.setdefault(entity, {})['question'] = res.content
    i += 1
    print(f"\rОбработано {i} из {len(set(matches))} пропусков")

with open('schema.json', 'w', encoding='utf-8') as json_file:
    json.dump(fill_dict, json_file, indent=4)

print("ВОПРОСЫ СГЕНЕРИРОВАНЫ.")