from enum import Enum

from nio.block.mixins import EnrichSignals
from nio.properties import StringProperty, Property, SelectProperty
from nio.util.discovery import discoverable

from .rethinkdb_base_block import RethinkDBBase


class ConflictBehavior(Enum):
    error = 'error'
    replace = 'replace'
    update = 'update'


@discoverable
class RethinkDBInsert(RethinkDBBase, EnrichSignals):

    """a block for updating info in a RethinkDB table"""

    table = StringProperty(title="Table to insert into", default='test',
                           allow_none=False)
    object = Property(title='Dictionary data to insert',
                      default='{{ $.to_dict() }}',
                      allow_none=False)
    conflict = SelectProperty(ConflictBehavior, title='Conflict behavior',
                              default=ConflictBehavior.error)

    def __init__(self):
        super().__init__()
        # current table being inserted into
        self._table = None

    def configure(self, context):
        super().configure(context)
        self._set_table()

    def process_signals(self, signals):
        notify_list = []
        for signal in signals:
            self.logger.debug('Insert is Processing signal: {}'.format(signal))

            # update incoming signals with results of the insert
            result = self.insert(signal)
            out_sig = self.get_output_signal(result, signal)
            self.logger.debug(out_sig)
            notify_list.append(out_sig)

        self.notify_signals(notify_list)

    def insert(self, signal):
        """filter by given fields and insert the correct document in the
        table
        """
        data = self.object(signal)

        insert_result = self._table.insert(data, conflict=self.conflict().value) \
            .run(self._connection)

        self.logger.debug("Sent insert request, result: {}"
                          .format(insert_result))

        if insert_result['errors'] > 0:
            # only first error is collected
            self.logger.error('Error inserting into table: {}'
                              .format(insert_result['first_error']))
        else:
            # if no errors, there should only be integer result fields, which
            # should sum to greater than 0 if anything was replaced, updated,
            # etc.
            if not sum(value for value in insert_result.values()
                       if isinstance(value, int)):
                # nothing changed
                self.logger.debug('nothing to be inserted')

        return insert_result

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
