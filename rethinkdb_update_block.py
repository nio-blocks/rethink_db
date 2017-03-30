import rethinkdb as rdb
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import StringProperty, PropertyHolder, Property
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

    def _locked_process_signals(self, signals):
        notify_list = []
        for signal in signals:
            self.logger.debug('Update is Processing signal: {}'.format(signal))
            # update incoming signals with results of the update
            result = self.execute_with_retry(self._update, signal)
            out_sig = self.get_output_signal(result, signal)
            self.logger.debug(out_sig)
            notify_list.append(out_sig)
        self.notify_signals(notify_list)

    def _update(self, signal):
        """filter by given fields and update the document in the table"""
        data = self.object(signal)
        # rethink does not allow updating of id.
        if 'id' in data:
            data.pop('id')
        with rdb.connect(
                host=self.host(),
                port=self.port(),
                db=self.database_name(),
                timeout=self.connect_timeout().total_seconds()) as conn:
            result = rdb.db(self.database_name()).table(self.table()).\
                filter(self.filter(signal)).update(data).run(conn)
        self.logger.debug("Sent update request, result: {}".format(result))
        if result['errors'] > 0:
            # only first error is collected
            self.logger.error(
                'Error updating table: {}'.format(result['first_error']))
        return result
