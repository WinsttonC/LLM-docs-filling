import re
import os

from dotenv import load_dotenv
load_dotenv()

doc_path = os.getenv("DOCUMENTS_PATH")

def is_valid_string(input_string):
    pattern = r'^[_. ]+$'
    return not bool(re.match(pattern, input_string))

def shorten_blanks(input_string):
    # Паттерн для поиска длинных пропусков
    
    if is_valid_string(input_string):
        pattern = r'(_{2,})'
        # Заменяем длинные пропуски на сокращенный вариант
        output_string = re.sub(pattern, '___', input_string)
        
        return output_string
    else:
        return ''

def find_blank_spots(text):
    pattern = r'_+'  # Шаблон для поиска одного или более подчеркиваний
    matches = re.finditer(pattern, text)
    
    results = []
    for match in matches:
        start = match.start()
        end = match.end()
        results.append((start, end))
        
    return results

def replace_substrings(input_string, fields_dict):
    # Паттерн для поиска подстрок вида [[...]]
    pattern = r'\[\[(.*?)\]\]'
    
    # Функция замены подстрок
    def replace_value(match):
        key = match.group(1)  # Содержимое внутри [[...]]
        # return fields_dict[key].get('user_answer', f'[[{key}]]') #replacement_dict[key]  # Возвращаем значение из словаря или оставляем как есть
        return fields_dict.get(key, f'[[{key}]]') #TODO: check (app-> fill rules)
    # Заменяем подстроки с помощью регулярных выражений и функции замены
    result_string = re.sub(pattern, replace_value, input_string)
    
    return result_string



def check_doc_existance(doc_name):
    file_path = f'{doc_path}/documents/{doc_name}.docx'
    if os.path.exists(file_path):
        return True
    else:
        return False
def check_schema_existance(doc_name):
    file_path = f'{doc_path}/doc_schemas/{doc_name}.json'
    # file_path = f'doc_schemas/{doc_name}'
    if os.path.exists(file_path):
        return True
    else:
        return False