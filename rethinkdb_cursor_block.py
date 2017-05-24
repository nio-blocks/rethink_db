from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import StringProperty, PropertyHolder, Property
from nio.util.discovery import discoverable
from .rethinkdb_base_block import RethinkDBBase


@discoverable
class RethinkDBCursor(RethinkDBBase, EnrichSignals):

    """a block for querying a rethinkdb table and adding results onto
    incoming signals"""

    table = StringProperty(title="Table to query", default='test',
                           allow_none=False)
    filter = Property(title='Filter by given fields',
                      default='{{ $.to_dict() }}',
                      allow_none=False)

    def __init__(self):
        super().__init__()
        # current table being queried
        self._table = None

    def configure(self, context):
        super().configure(context)
        self._set_table()

    def process_signals(self, signals):
        notify_list = []
        for signal in signals:
            self.logger.debug('Cursor is Processing signal: {}'.format(signal))

            # update incoming signals with results of the query
            results = self.query_table(signal)
            for result in results:
                out_sig = self.get_output_signal(result, signal)
                notify_list.append(out_sig)

        self.notify_signals(notify_list)

    def query_table(self, signal):
        filter = self._table.filter(self.filter(signal))
        cursor = filter.run(self._connection)

        self.logger.debug("Querying using filter: {}".format(filter))

        results = list(cursor)
        cursor.close()

        return results

    def _set_table(self):
        """set _table to a table object tied to the current db"""
        self._table = self._db.table(self.table())
