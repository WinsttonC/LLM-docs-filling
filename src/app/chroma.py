import chromadb
from chromadb.api.types import EmbeddingFunction, QueryResult


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
