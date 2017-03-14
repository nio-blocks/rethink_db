import rethinkdb as rdb
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import StringProperty, PropertyHolder, Property
from nio.util.discovery import discoverable
from .rethinkdb_base_block import RethinkDBBase


@discoverable
class RethinkDBFilter(RethinkDBBase, EnrichSignals):

    """a block for querying a rethinkdb table and adding results onto
    incoming signals"""

    table = StringProperty(title="Table to query", default='test',
                           allow_none=False)
    filter = Property(title='Filter by given fields',
                      default='{{ $.to_dict() }}',
                      allow_none=False)

    def _locked_process_signals(self, signals):
        notify_list = []
        for signal in signals:
            self.logger.debug('Filter is Processing signal: {}'.format(signal))
            # update incoming signals with results of the query
            results = self.execute_with_retry(self._filter, signal)
            if results:
                for result in results:
                    out_sig = self.get_output_signal(result, signal)
                    notify_list.append(out_sig)
            else:
                # always notify a signal. still append empty results to
                # enriched signals
                out_sig = self.get_output_signal(results, signal)
                notify_list.append(out_sig)

        self.notify_signals(notify_list)

    def _filter(self, signal):
        with rdb.connect(
                host=self.host(),
                port=self.port(),
                db=self.database_name(),
                timeout=self.connect_timeout().total_seconds()) as conn:
            cursor = rdb.db(self.database_name()).table(self.table()).\
                filter(self.filter(signal)).run(conn)
            results = list(cursor)
            cursor.close()
        self.logger.debug(
            "Querying using filter {} return results {}".format(
                self.filter(signal), results))
        return results
