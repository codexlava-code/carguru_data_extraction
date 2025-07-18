from apps.config import CONFIG

class DBConfig:
    def __init__(self):
        self.db_username = CONFIG.get("dbUsername")
        self.db_password = CONFIG.get("dbPassword")
        self.db_name = CONFIG.get("dbName")
        self.db_endpoint = CONFIG.get("dbHost")
        self.port = CONFIG.get("dbPort")
