import rethinkdb as rdb

from nio.block.base import Block
from nio.command import command
from nio.properties import (IntProperty, StringProperty, VersionProperty,
                            TimeDeltaProperty)
from nio.util.discovery import not_discoverable


@command("Get server info", method="_get_server_info")
@command("Reconnect to server", method="_reconnect_connection")
@command("List server databases", method="_get_list_of_databases")
@command("List database tables", method="_get_list_of_tables")
@not_discoverable
class RethinkDBBase(Block):

    """
    A block for communicating with a RethinkDB server.

    Properties:
        host (str): server host to connect to
        port (int): port on the server host, default rethink port is 28015
        database_name (str): database name to access
        connect_timeout (interval): amount of time to wait for a successful connection
    """

    version = VersionProperty('1.0.0')
    host = StringProperty(title='Host', default='[[RETHINKDB_HOST]]')
    port = IntProperty(title='Port', default='[[RETHINKDB_PORT]]')
    database_name = StringProperty(title='DB name', default='test')
    connect_timeout = TimeDeltaProperty(title="Connect timeout",
                                        default={"seconds": 20},
                                        visible=False)

    def __init__(self):
        super().__init__()
        # current connection to server
        self._connection = None
        # current database
        self._db = None
        # list of databases on current server
        self._database_name_list = None
        # list of tables on the database
        self._table_name_list = None

    def configure(self, context):
        super().configure(context)
        self._connect_to_db()

    def stop(self):
        self.logger.info('closing RethinkDB connection...')
        self._close_connection()
        super().stop()

    def _connect_to_db(self):
        """form a connection to a database, storing the connection for use
        in queries, etc. later on. Also form the database that this connection
        will use.
        """
        self.logger.debug('Connecting to DB...')
        self._connection = rdb.connect(host=self.host(),
                                       port=self.port(),
                                       db=self.database_name(),
                                       timeout=self.connect_timeout().total_seconds()
                                       )
        self._db = rdb.db(self.database_name())

    def _reconnect_connection(self):
        """close and attempt to reconnect to the existing connection"""
        self.logger.debug('Attempting to reconnect to DB...')
        self._connection.reconnect(
            timeout=self.connect_timeout().total_seconds())

    def _close_connection(self):
        """close the current connection"""
        self._connection.close(noreply_wait=True)

    def _get_server_info(self):
        """returns info about the current connected server"""
        return self._connection.server()

    def _get_list_of_databases(self):
        """returns a list of database names on the current server and sets it
        to self._database_name_list
        """
        self._database_name_list = rdb.db_list().run(self._connection)
        return self._database_name_list

    def _get_list_of_tables(self):
        """returns a list of tables for the current database and sets it to
        self._table_name_list
        """
        self._table_name_list = self._db.table_list().run(self._connection)
        return self._table_name_list
