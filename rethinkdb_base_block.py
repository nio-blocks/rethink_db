import rethinkdb as rdb
from nio.block.base import Block
from nio.block.mixins import Retry, LimitLock
from nio.properties import (IntProperty, StringProperty, VersionProperty,
                            TimeDeltaProperty)
from nio.util.discovery import not_discoverable


@not_discoverable
class RethinkDBBase(LimitLock, Retry, Block):

    """
    A block for communicating with a RethinkDB server.

    Properties:
        host (str): server host to connect to
        port (int): port on the server host, default rethink port is 28015
        database_name (str): database name to access
        connect_timeout (interval): time to wait for a successful connection
    """

    version = VersionProperty('1.0.0')
    host = StringProperty(title='Host', default='[[RETHINKDB_HOST]]')
    port = IntProperty(title='Port', default='[[RETHINKDB_PORT]]')
    database_name = StringProperty(title='DB name', default='test')
    connect_timeout = TimeDeltaProperty(
        title="Connect timeout", default={"seconds": 20}, visible=False)

    def process_signals(self, signals):
        self.execute_with_lock(
            self._locked_process_signals, 10, signals=signals)

    def _locked_process_signals(self, signals):
        pass
