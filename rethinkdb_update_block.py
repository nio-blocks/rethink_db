from nio.properties import StringProperty
from nio.util.discovery import discoverable
from nio.command import command
from .rethinkdb_base_block import RethinkDBBase


@discoverable
@command("List of indexes on current table", method="_get_list_of_indexes")
class RethinkDBUpdate(RethinkDBBase):

    table = StringProperty(title="Table to update", default='test')
    index_to_update = StringProperty(title="Table index to update",
                                     default='test')

    def __init__(self):
        super().__init__()
        # current table being updated
        self._table = None
        # list of all secondary indexes on the table
        self._list_of_indexes = None

    def configure(self, context):
        super().configure(context)
        self._set_table()
        self._get_list_of_indexes()

    def process_signals(self, signals):
        for signal in signals:
            self.logger.info('Processing signal: {}'.format(signal))
            self.update_table(signal)
        self.notify_signals(signals)

    def update_table(self, signal):
        data = {
            self.index_to_update(): signal.to_dict()[self.index_to_update()]
        }

        self._table.update(data).run(self._connection)

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())

    def _get_list_of_indexes(self):
        """gets the list of all secondary indexes on the current table and
        sets it to self._list_of_indexes
        """
        self._list_of_indexes = self._table.index_list().run(self._connection)
        return self._list_of_indexes
