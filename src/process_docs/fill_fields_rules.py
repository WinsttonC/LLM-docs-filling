from utils import replace_substrings

with open("schema.json", "r", encoding='utf-8') as f:
    schema = json.load(f)

str_document = Document('example.docx')
str_document = [p.text for p in str_document.paragraphs]

for line in str_document:
    line = replace_substrings(line, schema)

final_document = Document()

# Добавляем абзац с текстом в документ\
for text_block in str_document:
    final_document.add_paragraph(text_block)

# Сохраняем документ
final_document.save('final_document.docx')