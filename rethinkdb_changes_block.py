from nio.properties import StringProperty
from nio.signal.base import Signal
from nio.util.threading import spawn
from rethinkdb.net import DefaultCursorEmpty

from .rethinkdb_base_block import RethinkDBBase


class RethinkDBChanges(RethinkDBBase):
    """block to watch for changes from a RethinkDB and pass along any specified
    attributes
    """
    table = StringProperty(title="Table to watch", default='test',
                           allow_none=False)

    def __init__(self):
        super().__init__()
        # current table being updated
        self._table = None
        self._watch_thread = None
        self._change_feed = None

    def configure(self, context):
        super().configure(context)
        self._set_table()

    def start(self):
        super().start()
        self._watch_thread = spawn(self.watch_for_changes)

    def stop(self):
        self._change_feed.close()
        self._watch_thread.join(1)
        self.logger.debug('joined watch thread successfully')
        super().stop()

    def watch_for_changes(self):
        self._change_feed = self._table.changes(squash=True).run(self._connection)
        self.logger.debug('change feed: {}'.format(self._change_feed))

        while True:
            # wait for the next change. If the block is shutting down, change
            # will return an error, which will end the wait loop. An error such
            # as a connection error will also end this event loop. If no
            # exception, notify the change.
            try:
                change = self._change_feed.next(wait=True)
            except:
                if isinstance(self._change_feed.error, DefaultCursorEmpty):
                    # block is shutting down
                    pass
                else:
                    # a different error
                    self.logger.exception('Could not get change.')
                break
            else:
                self.logger.debug('Change: {}'.format(change))
                self.notify_signals(Signal(change['new_val']))

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
