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
        # current table being updated
        self._table = None
        self._watch_thread = None
        self._change_feed = None

    def configure(self, context):
        super().configure(context)
        self._set_table()
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
            try:
                change = self._change_feed.next(wait=True)
            except:
                self.logger.exception('Could not get change (ignore if this '
                                      'block is stopping)')
                break
            else:
                self.logger.debug(change)
                self.notify_signals(Signal(change['new_val']))

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
