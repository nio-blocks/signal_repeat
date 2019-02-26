from collections import defaultdict
from copy import copy
from nio import Block
from nio.block import input
from nio.block.mixins import GroupBy
from nio.modules.scheduler import Job
from nio.properties import VersionProperty, IntProperty, TimeDeltaProperty
from threading import Lock


@input('repeat', default=True, order=1)
@input('cancel', order=2)
class SignalRepeater(GroupBy, Block):

    version = VersionProperty('0.1.1')
    max_repeats = IntProperty(title='Max Repeats', default=-1)
    interval = TimeDeltaProperty(
        title='Repeat Interval', default={'seconds': 10})

    def configure(self, context):
        super().configure(context)
        self.notifications = defaultdict(dict)
        self._group_locks = defaultdict(Lock)

    def stop(self):
        for group in copy(self.notifications):
            self._cancel_group_job(group)
        super().stop()

    def _cancel_group_job(self, group):
        job = self.notifications[group].get('job')
        if job:
            self.logger.debug("Cancelling job for group {}".format(group))
            job.cancel()
            del self.notifications[group]

    def process_group_signals(self, signals, group, input_id='repeat'):
        if input_id == 'cancel':
            self._cancel_group_job(group)
            return
        if len(signals) == 0:
            return
        signal = signals[-1]
        repeats_remaining = self.max_repeats(signal)
        with self._group_locks[group]:
            self._cancel_group_job(group)
            if repeats_remaining == 0:
                # They don't want to repeat, ignore
                return
            self.logger.debug("Setting up repeat for group {}".format(group))
            self.notifications[group]['signal'] = signal
            self.notifications[group]['num_remaining'] = repeats_remaining
            self.notifications[group]['job'] = Job(
                target=self.notify_group,
                delta=self.interval(signal),
                repeatable=True,
                group=group)

    def notify_group(self, group):
        with self._group_locks[group]:
            notification = self.notifications[group]
            if notification.get('num_remaining', 0) != 0:
                notification['num_remaining'] -= 1
                self.logger.debug(
                    "Notifying signal for group {}, {} remaining".format(
                        group, notification['num_remaining']))
                self.notify_signals([notification['signal']])
            else:
                self._cancel_group_job(group)
