SignalRepeater
=======
Repeat incoming signals every interval, up to a max number of times.

This block operates similar to the queue block except that the timing is based off of incoming signals, rather than the start of the service. Whenever a signal comes in, it will start a timer and get repeated at timer expiration. This will continue until the max number of repeats is hit.

New signals that come in restart the counter and timer and replace the signal that is repeated.

There is also a `cancel` input that lets you cancel a repeat job.

Note: Signals are not "repeated" immediately when they come in - to achieve this behavior simply add a path that bypasses this block in your service.

Properties
----------
 * **Repeat Interval** - How often to repeat the notification of the incoming signal
 * **Max Repeats** - The maximum number of times to repeat the incoming signal. Defaults to `-1` which means repeat indefinitely.

Inputs
------
 * **repeat** - Signals to be repeated
 * **cancel** - Trigger a cancellation of an existing repeat

Example
-------
Imagine a block with **Max Repeats** = `2` and a **Repeat Interval** of 1 second. The following timing demonstrates the behavior of the block. Incoming signals are on top of the timeline, outgoing signals are on the bottom:
```
                                           (cancel)
    A               B     C             D     |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
        A   A           B     C   C         D
```
