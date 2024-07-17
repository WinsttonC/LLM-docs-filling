import chromadb
from chromadb.api.types import EmbeddingFunction, QueryResult
from chromadb.utils import embedding_functions

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



class Chroma:
    def __init__(
        self,
        path: str,
        embedding: EmbeddingFunction,
        collection_name: str,
    ) -> None:
        """
        Инициализирует класс для работы с ChromaDB. Используется для первоначальной загрузки данных в БД.
        Args:
            embedding (EmbeddingFunction): функция эмбеддинга.
            collection_name (str): название коллекции в ChromaDB.

        """
        self.embedding = embedding
        self.collection_name = collection_name
        self.chroma_client = chromadb.PersistentClient(path=path)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, embedding_function=self.embedding
        )

    def add_docs(self, data_dict: dict) -> None:
        """
        Добавляет документы в базу данных.
        Args:
            data_dict (dict): словарь, представляющий документы. Должен иметь поля docs, sources, questions, ids

        """
        docs = data_dict["docs"]
        # sources = data_dict["sources"]
        # questions = data_dict["questions"]
        ids = data_dict["ids"]
        # metadatas = [
        #     {"source": sources[i], "question": questions[i]} for i in range(len(docs))
        # ]

        start = 0
        end = len(docs)
        while start < end:
            self.collection.add(
                documents=docs[start : start + 100],
                # metadatas=metadatas[start : start + 100],
                ids=ids[start : start + 100],
            )

            start += 100

    def get_relevant_docs(self, query: str) -> QueryResult:
        """
        Получает документы из ChromaDB, удовлетворяющие пользовательскому запросу.
        Args:
            query (str): пользовательский запрос.
            collection_name (str): название коллекции ChromaDB, где находятся документы.
            embedding_info (dict): информация об эмбеддинге.
        Returns:
            Объект QueryResult с аттрибутами metadatas, documents и distances.

        """

        # chroma_client = chromadb.HttpClient(host="ca_case_tinkoff_chroma_db", port=8000)

        collection = self.collection
        if collection.count() > 0:
            return collection.query(
                query_texts=query,
                include=["metadatas", "documents", "distances"],
                n_results=5,
            )
        else:
            return collection.query(
                query_texts=query,
                include=["metadatas", "documents", "distances"],
                n_results=1,
            )

def find_documents(question):
    client = Chroma(f"{doc_path}/vect_docs", embedding_model, collection_name)

    docs = client.get_relevant_docs(question)
    docs = [
        doc
        for doc, distance in zip(docs["documents"][0], docs["distances"][0])
        if distance < 0.8  # TODO
    ]

    return docs


def add_documents_to_vectorstore(doc_name):
    client = Chroma(f"{doc_path}/vect_docs", embedding_model, collection_name)

    document_titles = [doc_name]

    data_dict = {
        "docs": document_titles,
    }

    client.add_docs(data_dict)