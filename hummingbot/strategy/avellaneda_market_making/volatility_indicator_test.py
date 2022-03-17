import math
import unittest
from volatility_indicator import VolatilityIndicator, RollingVolatilityIndicator
import statistics as s


class TestVolatilityIndicator(unittest.TestCase):
    def setUp(self):
        ticks = 60
        self._volatility = VolatilityIndicator(sampling_length = ticks)
        for i in range(int(ticks / 2)):
            self._volatility.add_sample(1.01)
            self._volatility.add_sample(1 / 1.01)

    def test_seconds(self):
        self.assertTrue(self._volatility.is_full())
        self.assertAlmostEqual(round(self._volatility.value(1), 5), .02007)

    def test_seconds_2(self):
        self.assertAlmostEqual(self._volatility.value(2), 0)

    def test_seconds_3(self):
        self.assertAlmostEqual(round(self._volatility.value(3), 5), .02044)

    # error if requesting more data than we can generate an estimate for
    def test_seconds_out_of_bounds(self):
        ret = self._volatility.value(120)
        # print(f"ret = {ret}")
        self.assertTrue(math.isnan(ret))

    # volatility should be returned as a percentage basis (insensitive to price)
    def test_volatility_of_linear_trend_is_zero(self):
        _volatility = VolatilityIndicator(sampling_length = 3)
        _volatility.add_sample(10)
        _volatility.add_sample(20)
        _volatility.add_sample(40)
        self.assertAlmostEqual(round(_volatility.value(1), 7), 1.4142136)

    def test_volatility_is_percentage(self):
        _volatility = VolatilityIndicator(sampling_length = 4)
        _volatility.add_sample(10)
        _volatility.add_sample(20)
        _volatility.add_sample(10)
        _volatility.add_sample(5)
        self.assertAlmostEqual(round(_volatility.value(1), 7), 0.8660254)


class TestRollingVolatilityIndicator(unittest.TestCase):
    def test_values(self):
        ticks = 1000
        # fill array with random values with standard deviation of 1
        n = s.NormalDist(mu=1, sigma=1)
        samples = n.samples(ticks, seed=42)
        # print(samples)
        print(s.mean(samples))
        print(s.stdev(samples))

        self._volatility = RollingVolatilityIndicator(sampling_length=600)
        for x in samples:
            self._volatility.add_sample(x)

        # Std deviation is a percentage so it should be much higher than 1
        vol1 = self._volatility.value(1)
        print(f"volatility-1={vol1}")
        self.assertGreater(vol1, 50)

        # Volatility should decline as the time periods get longer
        vol5 = self._volatility.value(5)
        print(f"volatility-5={vol5}")
        self.assertGreater(vol5, 8)
        self.assertGreater(vol1, vol5)

        # 10 sec
        vol10 = self._volatility.value(10)
        print(f"volatility-10={vol10}")
        self.assertGreater(vol10, 8)
        self.assertGreater(vol5, vol10)

        # 30 sec
        vol30 = self._volatility.value(30)
        print(f"volatility-30={vol30}")
        self.assertGreater(vol30, 2)
        self.assertGreater(vol10, vol30)

        # 60 sec
        vol60 = self._volatility.value(60)
        print(f"volatility-60={vol60}")
        self.assertGreater(vol60, 2)
        self.assertGreater(vol30, vol60)
