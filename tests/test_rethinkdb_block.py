from unittest.mock import patch, MagicMock

from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..rethinkdb_changes_block import RethinkDBChanges
from ..rethinkdb_update_block import RethinkDBUpdate
from ..rethinkdb_delete_block import RethinkDBDelete
from ..rethinkdb_filter_block import RethinkDBFilter
from ..rethinkdb_insert_block import RethinkDBInsert


class TestRethinkDBUpdateBlock(NIOBlockTestCase):

    def test_process_signals(self):
        blk = RethinkDBUpdate()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1',
                                   'exclude_existing': False})
        self.table_config = {
            "primary_key": "id"
        }

        blk.update_table = MagicMock(return_value={'result': 1})
        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.\
                config.return_value = self.table_config
            mock_rdb.db.return_value.table.return_value.filter.return_value.\
                update.return_value.run.return_value = {"errors": 0}
            blk.process_signals([Signal({'id': 1, 'test': 1})])
        blk.stop()
        # original input signal and output signal
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            "errors": 0,
        })

    def test_process_signals_using_get(self):
        blk = RethinkDBUpdate()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1',
                                   'exclude_existing': False})
        self.table_config = {
            "primary_key": "id"
        }

        blk.update_table = MagicMock(return_value={'result': 1})
        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.\
                config.return_value = self.table_config
            # mock .get() rather than .filter()
            mock_rdb.db.return_value.table.return_value.get.return_value.\
                update.return_value.run.return_value = {"errors": 0}
            blk.process_signals([Signal({'id': 1})])
        blk.stop()
        # original input signal and output signal
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            "errors": 0,
        })


class TestRethinkDBChangesBlock(NIOBlockTestCase):

    def test_gets_changes(self):
        blk = RethinkDBChanges()
        self.configure_block(blk, {'port': 8888, 'host': '127.0.0.1'})

        d = {'new_val': {'test_val': 1}}
        from threading import Event
        self.feed_complete = Event()
        self.changes = [{"new_val": {"new": "thing"}},
                        {"new_val": {"another": "thing"}}]

        def change_feed(wait):
            if self.changes:
                change = self.changes[0]
                self.changes = self.changes[1:]
                return change
            else:
                # Set cursor to empty so change feed thread in block returns
                self.feed_complete.set()
                from rethinkdb.net import DefaultCursorEmpty
                self.mock_change_feed.error = DefaultCursorEmpty()
                raise Exception
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.changes.return_value.\
                run.return_value.next.side_effect = change_feed
            self.mock_change_feed = mock_rdb.db.return_value.\
                table.return_value.changes.return_value.run.return_value
            blk.start()
            self.feed_complete.wait(1)
        blk.stop()
        self.assert_num_signals_notified(2)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            "another": "thing",
        })


class TestRethinkDBDeleteBlock(NIOBlockTestCase):

    def test_process_signals(self):
        blk = RethinkDBDelete()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        self.table_config = {
            "primary_key": "id"
        }

        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.\
                config.return_value = self.table_config
            mock_rdb.db.return_value.table.return_value.filter.return_value. \
                delete.return_value.run.return_value = {"errors": 0,
                                                        "changes": {},
                                                        "deleted": 1}
            blk.process_signals([Signal({'id': 1, 'test': 1})])
        blk.stop()

        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            "errors": 0,
            "changes": {},
            "deleted": 1
        })

    def test_process_signals_using_get(self):
        blk = RethinkDBDelete()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        self.table_config = {
            "primary_key": "id"
        }

        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.\
                config.return_value = self.table_config
            mock_rdb.db.return_value.table.return_value.get.return_value. \
                delete.return_value.run.return_value = {"errors": 0,
                                                        "changes": {},
                                                        "deleted": 1}
            blk.process_signals([Signal({'id': 1})])
        blk.stop()

        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            "errors": 0,
            "changes": {},
            "deleted": 1
        })


class TestRethinkDBFilterBlock(NIOBlockTestCase):

    def test_process_signals(self):
        blk = RethinkDBFilter()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        self.table_config = {
            "primary_key": "id"
        }

        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.\
                config.return_value.run.return_value = self.table_config
            mock_rdb.db.return_value.table.return_value.filter.return_value.\
                run.return_value = [{"id": 8, 'test': 7, 'test1': 7},
                                    {'id': 8, 'test': 7, 'test2': 6},
                                    {"id": 8, 'test': 7, 'test3': 5}]
            blk.process_signals([Signal({'id': 8, 'test': 7})])
        blk.stop()
        # original input signal and output signal
        self.assert_num_signals_notified(3)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            'id': 8,
            'test': 7,
            'test3': 5})

    def test_process_signals_using_get(self):
        blk = RethinkDBFilter()
        self.configure_block(blk, {'port': 8888,
                                   'host': '127.0.0.1'})
        self.table_config = {
            "primary_key": "id"
        }

        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.\
                config.return_value.run.return_value = self.table_config
            mock_rdb.db.return_value.table.return_value.get.return_value.\
                run.return_value = [{"id": 8, 'test': 7, 'test1': 7},
                                    {'id': 8, 'test': 7, 'test2': 6},
                                    {"id": 8, 'test': 7, 'test3': 5}]
            blk.process_signals([Signal({'id': 8})])
        blk.stop()
        # original input signal and output signal
        self.assert_num_signals_notified(3)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            'id': 8,
            'test': 7,
            'test3': 5})


class TestRethinkDBInsertBlock(NIOBlockTestCase):

    def test_process_signal(self):
        blk = RethinkDBInsert()
        self.configure_block(blk, {'port': 8888, 'host': '127.0.0.1'})
        blk.start()
        with patch(blk.__module__ + '.rdb') as mock_rdb:
            mock_rdb.db.return_value.table.return_value.insert.return_value.\
                run.return_value = {"errors": 0}
            blk.process_signals([Signal({'id': 1, 'test': 1})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_signal_notified().to_dict(), {
            "errors": 0})
