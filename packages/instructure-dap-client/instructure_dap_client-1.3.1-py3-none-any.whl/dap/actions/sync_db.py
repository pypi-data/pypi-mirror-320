from ..api import DAPClient
from ..dap_types import Credentials
from ..integration.database import DatabaseConnection
from ..replicator.sql import SQLReplicator


async def sync_db(
    base_url: str,
    credentials: Credentials,
    connection_string: str,
    namespace: str,
    table_name: str,
) -> None:
    db_connection = DatabaseConnection(connection_string)
    async with DAPClient(base_url, credentials) as session:
        await SQLReplicator(session, db_connection).synchronize(namespace, table_name)
