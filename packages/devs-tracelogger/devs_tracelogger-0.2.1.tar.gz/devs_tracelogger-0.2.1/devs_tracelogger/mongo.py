from pymongo import MongoClient

class MongoLogger:
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str) -> None:
        """
        Inicializa o logger do MongoDB.

        Parâmetros:
        - mongo_uri (str): URI de conexão com o MongoDB.
        - db_name (str): Nome do banco de dados no MongoDB.
        - collection_name (str): Nome da coleção onde os logs serão armazenados.
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def log_error(self, error_data: dict) -> None:
        """
        Insere um log de erro no MongoDB.

        Parâmetros:
        - error_data (dict): Dicionário com as informações do erro a serem armazenadas.
        """
        self.collection.insert_one(error_data)
