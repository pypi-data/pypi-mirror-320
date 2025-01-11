import logging

from dap.api import DAPSession
from dap.integration.database import DatabaseConnection
from dap.replicator.sql_op import SqlOp
from dap.replicator.sql_op_drop import SqlOpDrop
from dap.replicator.sql_op_init import SqlOpInit
from dap.replicator.sql_op_sync import SqlOpSync
from dap.version_upgrade.db_version_upgrader import VersionUpgrader

logger: logging.Logger = logging.getLogger(__name__)


class SQLReplicator:
    """
    Encapsulates logic that replicates changes acquired from DAP API in a SQL database.
    """

    _session: DAPSession
    _connection: DatabaseConnection

    def __init__(self, session: DAPSession, connection: DatabaseConnection) -> None:
        self._session = session
        self._connection = connection

    async def initialize(
        self,
        namespace: str,
        table_name: str,
    ) -> None:
        logger.debug(f"initializing table: {namespace}.{table_name}")

        async with self._connection.connection as base_connection:
            explorer = self._connection.engine.create_explorer(base_connection)
            await VersionUpgrader(
                explorer, base_connection, self._connection.dialect
            ).upgrade()

            # Currently, in case of web logs, due to upstream 'at-least-once' logic,
            # sometimes we receive the same key twice or more times.
            # When we switch to the next-generation web logs that has no
            # duplicates by design, we can remove this line.
            use_upsert = namespace == "canvas_logs" and table_name == "web_logs"

            init_op: SqlOp = SqlOpInit(
                conn=base_connection,
                namespace=namespace,
                table_name=table_name,
                explorer=explorer,
                session=self._session,
                use_upsert=use_upsert,
            )

            await init_op.run()

    async def synchronize(
        self,
        namespace: str,
        table_name: str,
    ) -> None:
        logger.debug(f"synchronizing table: {namespace}.{table_name}")

        async with self._connection.connection as base_connection:
            explorer = self._connection.engine.create_explorer(base_connection)
            await VersionUpgrader(
                explorer, base_connection, self._connection.dialect
            ).upgrade()

            sync_op: SqlOp = SqlOpSync(
                conn=base_connection,
                namespace=namespace,
                table_name=table_name,
                explorer=explorer,
                session=self._session,
            )

            await sync_op.run()


class SQLDrop:
    """
    Encapsulates logic that drops a table from the SQL database.
    """

    _connection: DatabaseConnection

    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    async def drop(
        self,
        namespace: str,
        table_name: str,
    ) -> None:
        """
        Drops the given database table.
        """

        async with self._connection.connection as base_connection:
            explorer = self._connection.engine.create_explorer(base_connection)
            await VersionUpgrader(
                explorer, base_connection, self._connection.dialect
            ).upgrade()
            logger.debug(f"dropping table: {namespace}.{table_name}")

            drop_op: SqlOp = SqlOpDrop(
                conn=base_connection,
                namespace=namespace,
                table_name=table_name,
                explorer=explorer,
            )

            await drop_op.run()
