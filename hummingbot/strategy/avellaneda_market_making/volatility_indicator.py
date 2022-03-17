import math
import numpy as np

# This indicator stores historical prices at a tick level and will return volatility on demand
# for any timeframe within the buffer window. It is intended to be used to return volatility
# for different durations (-10s, -60s, -5 min) on a rolling basis. Volatility is smoothed to
# reduce the effect of small sample sizes. For non-smoothed volatility, use VolatilityIndicator.


class RollingVolatilityIndicator():
    def __init__(self, sampling_length = 600):
        # Set up dictionary of RingBuffers, each set to number of entries= sampling_length
        self._indicators = {1: RingBuffer(sampling_length),
                            5: RingBuffer(sampling_length),
                            10: RingBuffer(sampling_length),
                            20: RingBuffer(sampling_length),
                            30: RingBuffer(sampling_length),
                            40: RingBuffer(sampling_length),
                            50: RingBuffer(sampling_length),
                            60: RingBuffer(sampling_length),
                            120: RingBuffer(sampling_length),
                            180: RingBuffer(sampling_length),
                            600: RingBuffer(sampling_length),
                            }

        # Set up Volatility Indiciator
        self._volatility = VolatilityIndicator(sampling_length = sampling_length)

    def add_sample(self, value):
        self._volatility.add_sample(float(value))

        # Add new readings to RingBuffers
        for key in self._indicators:
            current_reading = self._volatility.value(key)
            if not math.isnan(current_reading):
                self._indicators[key].append(current_reading)

    def value(self, period: int):
        if period not in self._indicators:
            return math.nan
        array = self._indicators[period].get_as_numpy_array()
        if len(array) == 0:
            return math.nan
        return np.mean(array)

    def array(self, period: int):
        if period not in self._indicators:
            return math.nan
        array = self._indicators[period].get_as_numpy_array()
        return array


class VolatilityIndicator():
    # 10 minute default
    def __init__(self, sampling_length = 600):
        self._sampling_length = sampling_length
        self._sampling_buffer = RingBuffer(sampling_length)
        self._last: float = 0.0

    def add_sample(self, value: float):
        self._sampling_buffer.append(value)
        # if self._last == 0:
        #     self._last = value
        # else:
        #     self._sampling_buffer.append((value - self._last) / self._last)
        #     self._last = value

    # ticks is the number of seconds to calculate the volatility for, ie: 60 = 1 minute
    def value(self, ticks) -> float:
        if ticks > self._sampling_length:
            return math.nan

        # Get values for evenly spaced prices beginning from the most recent sample
        np_sampling_buffer = self._sampling_buffer.get_as_numpy_array()
        # print(np_sampling_buffer)
        subsamples = np_sampling_buffer[-1::-ticks]
        diff = np.subtract(subsamples[:-1], subsamples[1:])
        returns = np.true_divide(diff, subsamples[1:])

        if returns.size < 2:
            return math.nan

        vol = np.sqrt(np.sum(np.square(returns)) / (returns.size - 1))
        # print(f"subsamples len = {len(subsamples)}  samples={subsamples}  \n\n diff={diff} \n\n returns={np.sum(np.square(returns))}")
        return vol

    def is_full(self) -> bool:
        return self._sampling_buffer.is_full()

    def len(self) -> int:
        return self._sampling_buffer.len()


class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur + 1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:] + self.data[:self.cur]

        def is_full(self):
            return True

        def len(self):
            return len(self.data)

        def get_as_numpy_array(self):
            return np.array(self.data)

    def get_as_numpy_array(self):
        return np.array(self.data)

    def is_full(self):
        return False

    def len(self):
        return len(self.data)

    def append(self, x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        # print(f"len(self.data): {len(self.data)}  self.max:{self.max} ")
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data
