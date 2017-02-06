import rethinkdb as rdb
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

    def _locked_process_signals(self, signals):
        notify_list = []
        self.logger.debug('length of signals: {}'.format(len(signals)))
        for signal in signals:
            self.logger.debug('Insert is Processing signal: {}'.format(signal))
            # update incoming signals with results of the insert
            result = self.execute_with_retry(self._insert, signal)
            out_sig = self.get_output_signal(result, signal)
            self.logger.debug(out_sig)
            notify_list.append(out_sig)
        self.notify_signals(notify_list)

    def _insert(self, signal):
        """filter by given fields and insert the document in the table"""
        data = self.object(signal)
        with rdb.connect(
                host=self.host(),
                port=self.port(),
                db=self.database_name(),
                timeout=self.connect_timeout().total_seconds()) as conn:
            insert_result = \
                rdb.db(self.database_name()).table(self.table()).insert(
                    data, conflict=self.conflict().value).run(conn)
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
