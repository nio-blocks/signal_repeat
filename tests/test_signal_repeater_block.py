from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from nio.testing.modules.scheduler.scheduler import JumpAheadScheduler
from ..signal_repeater_block import SignalRepeater


class TestSignalRepeater(NIOBlockTestCase):

    def test_repeats(self):
        """ Test that the block repeats signals n times """
        blk = SignalRepeater()
        self.configure_block(blk, {
            'interval': {'seconds': 1},
            'max_repeats': 2,
        })
        blk.start()
        blk.process_signals([Signal({"hello": "nio"})])
        JumpAheadScheduler.jump_ahead(3)
        blk.stop()
        self.assert_num_signals_notified(2)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {"hello": "nio"})

    def test_repeats_indefinitely(self):
        """ Test that -1 max repeats means indefinitely """
        blk = SignalRepeater()
        self.configure_block(blk, {
            'interval': {'seconds': 1},
            'max_repeats': -1,
        })
        blk.start()
        blk.process_signals([Signal({"hello": "nio"})])
        JumpAheadScheduler.jump_ahead(3)
        blk.stop()
        self.assert_num_signals_notified(3)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {"hello": "nio"})

    def test_cancel(self):
        """ Test that repeats can be cancelled """
        blk = SignalRepeater()
        self.configure_block(blk, {
            'interval': {'seconds': 1},
            'max_repeats': 2,
        })
        blk.start()
        blk.process_signals([Signal({"hello": "nio"})])
        # After one second we have one of our repeats
        JumpAheadScheduler.jump_ahead(1)
        self.assert_num_signals_notified(1)
        # Send a signal to the cancel input
        blk.process_signals([Signal()], input_id='cancel')
        # Give it more time and make sure no signals came out
        JumpAheadScheduler.jump_ahead(5)
        self.assert_num_signals_notified(1)
        # Send another signal to the default input
        # and make sure it gets repeated again
        blk.process_signals([Signal({"hello": "nio"})])
        JumpAheadScheduler.jump_ahead(5)
        self.assert_num_signals_notified(3)
        blk.stop()

    def test_groups(self):
        """ Make sure we process signals in different groups separately """
        blk = SignalRepeater()
        self.configure_block(blk, {
            'interval': {'seconds': 1},
            'max_repeats': 2,
            'group_by': '{{ $group }}',
        })
        blk.start()
        blk.process_signals([Signal({"group": "A"})])
        JumpAheadScheduler.jump_ahead(1)
        self.assert_num_signals_notified(1)
        # Another group means another signal
        blk.process_signals([Signal({"group": "B"})])
        JumpAheadScheduler.jump_ahead(1)
        self.assert_num_signals_notified(3)
        # Group A is done at this point
        # Replacing group B resets its counter
        blk.process_signals([Signal({"group": "B"})])
        JumpAheadScheduler.jump_ahead(5)
        self.assert_num_signals_notified(5)  # 2 from A, 1+2 from B
        blk.stop()
