import rethinkdb as rdb

from nio.block.base import Block
from nio.command import command
from nio.properties import (IntProperty, StringProperty, VersionProperty,
                            TimeDeltaProperty)
from nio.util.discovery import not_discoverable, discoverable


@command("Get server info", method="_get_server_info")
@command("Reconnect to server", method="_reconnect_connection")
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
    port = IntProperty(title='Port', default=28015)
    database_name = StringProperty(title='DB name', default='test')
    connect_timeout = TimeDeltaProperty(title="Connect timeout",
                                        default={"seconds": 20},
                                        visible=False)

    def __init__(self):
        super().__init__()
        self._connection = None

    def configure(self, context):
        super().configure(context)
        self._connect_to_db()

    def stop(self):
        self.logger.info('closing RethinkDB connection...')
        self._close_connection()
        super().stop()

    def process_signals(self, signals):
        for signal in signals:
            self.logger.info('Processing signal: {}'.format(signal))
        self.notify_signals(signals)

    def _connect_to_db(self):
        """form a connection to a database, storing the connection for use
        in queries, etc. later on
        """
        self.logger.debug('Connecting to DB...')
        self._connection = rdb.connect(host=self.host(),
                                       port=self.port(),
                                       db=self.database_name(),
                                       timeout=self.connect_timeout().total_seconds()
                                       )

    def _reconnect_connection(self):
        """close and attempt to reconnect to the existing connection"""
        self.logger.debug('Attempting to reconnect to DB...')
        self._connection.reconnect(
            timeout=self.connect_timeout().total_seconds())

    def _close_connection(self):
        """close the current connection"""
        self._connection.close()

    def _get_server_info(self):
        """returns info about the current connected server"""
        return self._connection.server()


@discoverable
class RethinkDBUpdate(RethinkDBBase):

    table = StringProperty(title="Table to update", default='test')



class RethinkDBChanges(RethinkDBBase):
    pass
