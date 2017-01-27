from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.signal.base import Signal
from nio.properties import (StringProperty, ListProperty, PropertyHolder,
                            Property)
from nio.util.discovery import discoverable
from .rethinkdb_base_block import RethinkDBBase


class MatchItem(PropertyHolder):
    key = Property(title='Match key')


@discoverable
class RethinkDBUpdate(RethinkDBBase, EnrichSignals):

    """a block for updating info in a RethinkDB table"""

    table = StringProperty(title="Table to update", default='test',
                           allow_none=False)
    filter = Property(title='Filter dictionary',
                      default='{{ {"id": $id} }}',
                      allow_none=False)
    object = Property(title='Dictionary data to update',
                      default='{{ $.to_dict() }}',
                      allow_none=False)

    def __init__(self):
        super().__init__()
        # current table being updated
        self._table = None

    def configure(self, context):
        super().configure(context)
        self._set_table()

    def process_signals(self, signals):
        notify_list = []
        for signal in signals:
            self.logger.debug('Update is Processing signal: {}'.format(signal))

            # update incoming signals with results of the update
            result = self.update_table(signal)
            out_sig = self.get_output_signal(result, signal)
            self.logger.debug(out_sig)
            notify_list.append(out_sig)

        self.notify_signals(notify_list)

    def update_table(self, signal):
        """filter by given fields and update the correct document in the
        table
        """
        data = self.object(signal)
        # rethink does not allow updating of id.
        if 'id' in data:
            data.pop('id')
        filter_dict = self.filter(signal)
        self.logger.debug("Updating using filters: {}".format(filter_dict))

        result = \
            self._table.filter(filter_dict).update(data).run(self._connection)

        self.logger.debug("Sent update request, result: {}".format(result))

        if result['errors'] > 0:
            # only first error is collected
            self.logger.error('Error updating table: {}'
                              .format(result['first_error']))
        else:
            # if no errors, there should only be integer result fields, which
            # should sum to greater than 0 if anything was replaced, updated,
            # etc.
            if not sum(result.values()):
                # if 0, it did nothing, which means that it found no matches
                # with the given filters.
                self.logger.debug('(no document fields matching given filters)')

        return result

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
