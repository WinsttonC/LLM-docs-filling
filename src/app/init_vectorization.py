from chroma import Chroma
import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from utils import hash_filename
load_dotenv()

embedding_name = "text-embedding-3-large"
collection_name = 'embedding_name'
api_key=os.getenv("OPENAI_API_KEY")
api_base=os.getenv("BASE_URL_OPENAI_API")
folder_path = r'C:\Users\Winston\Downloads\Документы для тестового\Шаблоны'
                                                              
embedding_model = embedding_functions.OpenAIEmbeddingFunction(model_name=embedding_name,
                                                              api_key=api_key,
                                                              api_base=api_base,
                                                              )


client = Chroma("user_docs", embedding_model, collection_name)

files = os.listdir(folder_path)
document_titles = [os.path.splitext(file)[0] for file in files]



data_dict = {
    "docs": document_titles,
    "ids": [hash_filename(f) for f in document_titles]
}

client.add_docs(data_dict)
