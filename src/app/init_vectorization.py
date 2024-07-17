import os

from chromadb.utils import embedding_functions
from dotenv import load_dotenv

from chroma import Chroma
from utils import hash_filename

load_dotenv()

embedding_name = "text-embedding-3-large"
collection_name = "embedding_name"
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("BASE_URL_OPENAI_API")
doc_path = os.getenv("DOCUMENTS_PATH")

folder_path = f"{doc_path}/documents"

embedding_model = embedding_functions.OpenAIEmbeddingFunction(
    model_name=embedding_name,
    api_key=api_key,
    api_base=api_base,
)


client = Chroma(f"{doc_path}/vect_docs", embedding_model, collection_name)

files = os.listdir(folder_path)
document_titles = [os.path.splitext(file)[0] for file in files]


data_dict = {
    "docs": document_titles,
    "ids": [hash_filename(f) for f in document_titles],
}

client.add_docs(data_dict)
