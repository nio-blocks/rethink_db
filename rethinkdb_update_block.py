from nio.properties import (StringProperty, ListProperty, PropertyHolder,
                            Property)
from nio.util.discovery import discoverable
from .rethinkdb_base_block import RethinkDBBase


class MatchItem(PropertyHolder):
    key = Property(title='Match key')


@discoverable
class RethinkDBUpdate(RethinkDBBase):

    """a block for updating info in a RethinkDB table"""

    table = StringProperty(title="Table to update", default='test')
    filters = ListProperty(MatchItem, title='Match the following document keys',
                           default=[])

    def __init__(self):
        super().__init__()
        # current table being updated
        self._table = None

    def configure(self, context):
        super().configure(context)
        self._set_table()

    def process_signals(self, signals):
        for signal in signals:
            self.logger.debug('Processing signal: {}'.format(signal))
            self.update_table(signal)
        self.notify_signals(signals)

    def update_table(self, signal):
        """filter by given fields and update the correct document in the
        table
        """
        data = signal.to_dict()
        filter_dict = {}
        filters = (filter.key() for filter in self.filters())

        for key in filters:
            filter_dict.update({key: data[key]})

        self.logger.debug("Update using filters: {}".format(filter_dict))

        field_filter = self._table.filter(filter_dict)
        result = field_filter.update(data).run(self._connection)

        self.logger.debug("Sent update request, result: {}".format(result))
        if not sum(result.values()):
            self.logger.debug('(no document fields matching given filters)')

        self.notify_signals(result)

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
