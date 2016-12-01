from unittest import skip
from unittest.mock import patch, MagicMock

from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..rethinkdb_base_block import RethinkDBBase
from ..rethinkdb_changes_block import RethinkDBChanges
from ..rethinkdb_update_block import RethinkDBUpdate


@patch('rethinkdb.connect')
class TestRethinkDBBaseBlock(NIOBlockTestCase):

    def test_connection(self, mocked_connection):
        blk = RethinkDBBase()
        blk._db = MagicMock()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        blk.start()
        blk.stop()
        self.assertEqual(mocked_connection.call_count, 1)
        self.assertEqual(blk._connection.close.call_count, 1)
        self.assertEqual(blk._connection.reconnect.call_count, 0)
        self.assert_num_signals_notified(0)


@patch('rethinkdb.connect')
class TestRethinkDBUpdateBlock(NIOBlockTestCase):

    def test_process_signals(self, mocked_connection):
        blk = RethinkDBUpdate()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        blk.update_table = MagicMock(return_value={})
        blk.start()
        blk.process_signals([Signal({'test': 1})])
        blk.stop()
        self.assertEqual(blk.update_table.call_count, 1)
        # original input signal and output signal
        self.assert_num_signals_notified(2)


@skip
class TestRethinkDBChangesBlock(NIOBlockTestCase):

    def test_gets_changes(self):
        blk = RethinkDBChanges()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        d = {'new_val': {'test_val': 1}}
        blk._change_feed.next = MagicMock(return_value=d)
        blk.start()
        blk.stop()
        self.assertEqual(blk._change_feed.close.call_count, 1)
        self.assert_num_signals_notified(1)
