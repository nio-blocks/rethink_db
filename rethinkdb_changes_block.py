from datetime import timedelta

from nio.properties import StringProperty
from nio.util.scheduler.job import Job
from nio.signal.base import Signal

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
        self._watch_job = None

    def configure(self, context):
        super().configure(context)
        self._set_table()
        self._watch_job = Job(self.watch_for_changes, timedelta(0), False)

    def stop(self):
        self._watch_job.cancel()
        super().stop()

    def watch_for_changes(self):
        for change in self._table.changes(squash=True).run(self._connection):
            self.logger.debug(change)
            self.notify_signals(Signal(change['new_val']))

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
