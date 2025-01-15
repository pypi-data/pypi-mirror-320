import oracledb
import psycopg
import pymongo

from .configs import Configs


class _DBConnector:
    def __init__(self, connection_str, db_name):
        self.connection_str = connection_str
        self.db_name = db_name

    def postgresql(self):
        return psycopg.connect(f"{self.connection_str}/{self.db_name}")

    def mongodb(self):
        return pymongo.MongoClient(self.connection_str)[self.db_name]

    def oracle(self):
        return oracledb.connect(f"{self.connection_str}/{self.db_name}")


class _SQL:
    def __init__(self):
        self.db_connector = None

    def request(self, *args, **kwargs):
        return self.db_connector.execute(*args, **kwargs)

    def close(self):
        self.db_connector.close()


class _Postgresql(_SQL):
    def __init__(self, db_connector: _DBConnector):
        super().__init__()
        self.db_connector = db_connector.postgresql()


class _Oracle(_SQL):
    def __init__(self, db_connector: _DBConnector):
        super().__init__()
        self.db_connector = db_connector.oracle()


def connect(dbc_name):
    """Get a connection to the database connector named in the parameters.

    Args:
        dbc_name: the db connector name.

    Returns:
        :
            Connection to use .request() method or mongo database class.
    """
    api_client = Configs.instance.dbc_api_client
    response = api_client.request(
        "GET",
        f"/db-connectors/detail?db_name={dbc_name}&track_id="
        f"{Configs.instance.TRACK_ID}",
    )
    response.raise_for_status()
    response = response.json()

    db_type = response["db_type"]

    host_url = response["host"].split("/")
    conn_str = (
        f"{db_type}://{response['username']}:{response['password']}@"
        f"{host_url[0]}:{response['port']}/{host_url[1]}"
        if len(host_url) > 1
        else f"{db_type}://{response['username']}:{response['password']}@"
        f"{response['host']}:{response['port']}"
    )

    if db_type == "postgresql":
        conn = _Postgresql(_DBConnector(conn_str, response["database"]))
    elif db_type == "oracle":
        conn = _Oracle(_DBConnector(conn_str, response["database"]))
    elif db_type == "mongodb":
        # in case for mongodb need to verify dns as seen list or not.
        if response["port"] == 0:
            conn_str = (
                f"{db_type}+srv://{response['username']}:"
                f"{response['password']}@{response['host']}"
            )
        conn = _DBConnector(conn_str, response["database"]).mongodb()
    else:
        raise NotImplementedError(
            f"Connection to databases {db_type} is not yet available"
        )

    return conn
