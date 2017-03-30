import rethinkdb as rdb
from nio.properties import StringProperty, Property
from nio.util.discovery import discoverable
from .rethinkdb_base_block import RethinkDBBase
from nio.signal.base import Signal


@discoverable
class RethinkDBDelete(RethinkDBBase):

    """a block for deleting one or more documents from a rethinkdb table"""

    table = StringProperty(title="Table to query", default='test',
                           allow_none=False)
    filter = Property(title='Filter by given fields',
                      default='{{ $.to_dict() }}',
                      allow_none=False)

    def _locked_process_signals(self, signals):
        notify_list = []
        for signal in signals:
            self.logger.debug('Delete is Processing signal: {}'.format(signal))
            # update incoming signals with results of the query
            delete_results = self.execute_with_retry(self._delete, signal)
            self.logger.debug("Delete results: {}".format(delete_results))
            notify_list.append(Signal(delete_results))
        self.notify_signals(notify_list)

    def _delete(self, signal):
        with rdb.connect(
                host=self.host(),
                port=self.port(),
                db=self.database_name(),
                timeout=self.connect_timeout().total_seconds()) as conn:

            # this will return the typical deleted, errors, unchanges, etc.
            # as well as changes. If the delete was successful, 'new_val' will
            # be none in changes.
            results = rdb.db(self.database_name()).table(self.table()).\
                filter(self.filter(signal)).delete(return_changes=True).\
                run(conn)

        if results["deleted"] == 0:
            self.logger.debug("Unable to delete document for signal: {}"
                              .format(signal))

        self.logger.debug("Deleting using filter {} return results: {}"
                          .format(self.filter(signal), results))
        return results
