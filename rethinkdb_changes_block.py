import rethinkdb as rdb
from rethinkdb.net import DefaultCursorEmpty

from nio.properties import StringProperty
from nio.signal.base import Signal
from nio.util.threading import spawn

from .rethinkdb_base_block import RethinkDBBase


class RethinkDBChanges(RethinkDBBase):
    """block to watch for changes from a RethinkDB and pass along any specified
    attributes
    """
    table = StringProperty(title="Table to watch", default='test',
                           allow_none=False)

    def __init__(self):
        super().__init__()
        self._watch_thread = None

    def start(self):
        super().start()
        self._watch_thread = spawn(self.watch_for_changes)

    def stop(self):
        self._watch_thread.join(1)
        self.logger.debug('joined watch thread successfully')
        super().stop()

    def watch_for_changes(self):
        self.execute_with_retry(self._changes)

    def _changes(self):
        with rdb.connect(
                host=self.host(),
                port=self.port(),
                db=self.database_name(),
                timeout=self.connect_timeout().total_seconds()) as conn:
            change_feed = rdb.db(self.database_name()).table(self.table()).\
                changes(squash=True).run(conn)
            self.logger.debug('change feed: {}'.format(change_feed))
            while True:
                try:
                    change = change_feed.next(wait=True)
                except:
                    if isinstance(change_feed.error, DefaultCursorEmpty):
                        # block is shutting down
                        break
                    else:
                        # a different error
                        self.logger.exception('Could not get change')
                        raise
                else:
                    self.logger.debug('Change: {}'.format(change))
                    self.notify_signals(Signal(change['new_val']))
