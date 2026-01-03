from .trend_pullback_v1 import run_backtest as tp_backtest
from .trend_pullback_v1.config import StrategyParams as TPParams

from .breakout_v1 import run_backtest as bo_backtest
from .breakout_v1.config import StrategyParams as BOParams

STRATEGIES = {
    "trend_pullback_v1": (tp_backtest.run_backtest_for_default_universe, TPParams),
    "breakout_v1": (bo_backtest.run_backtest_for_default_universe, BOParams),
    # add others here
}