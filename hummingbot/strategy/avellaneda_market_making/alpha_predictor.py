from math import isnan
import pandas as pd
from statistics import NormalDist

# This class accepts a rolling volatility indicator, target spread, fee (%) and capture.
# Outputs a series of alpha predictions for each volatility timeframe as a dataframe.


class AlphaPredictor():
    def __init__(self, rolling_vol, target_spread: float, fee_pct: float, capture: float):

        if fee_pct is None:
            fee_pct = 0.1

        if capture is None:
            capture = .33

        # create dataframe
        df = pd.DataFrame()

        # for each timeframe
        for sec in range([5, 10, 20, 30, 40, 50, 60, 120, 180]):
            # Calculate z-score
            vol = rolling_vol.value(sec)
            if isnan(vol) or vol == 0:
                continue

            z = target_spread / vol

            # Convert to probability of placing a trade
            p = NormalDist().cdf(z) * 2

            # Calculate # of chances per 24h at this timeframe
            num_chances = 86400 / sec
            num_hits = num_chances * p

            # Calculate opportunity. This is the current target spread being considered.
            # TODO: Calculate alternative target spread such that probability doesn't drop under 50%
            # TODO: Return opportunity so caller can keep a running total
            opportunity = target_spread

            # Calculate total opportunity per 24 hours
            # total_opportunity = num_chances * opportunity

            # Calculate daily alpha
            alpha = (opportunity - fee_pct) * capture * num_hits

            df['sec'] = sec
            df['opportunity'] = opportunity
            df['alpha'] = alpha
