import enum

import empyrical as emp
from skfolio.measures import RiskMeasure
from skfolio.optimization import ObjectiveFunction

__all__ = ["DataPeriod", "SelectMode", "OptimizeObjective", "RiskMetric"]


class DataPeriod(enum.Enum):
    """Enum for periodicity of data.

    Attributes:
        DAILY: Daily periodicity.
        WEEKLY: Weekly periodicity.
        MONTHLY: Monthly periodicity.
        QUARTERLY: Quarterly periodicity.
        YEARLY: Yearly periodicity.
    """

    DAILY = emp.DAILY
    WEEKLY = emp.WEEKLY
    MONTHLY = emp.MONTHLY
    QUARTERLY = emp.QUARTERLY
    YEARLY = emp.YEARLY


class SelectMode(enum.Enum):
    """Enum for selection modes.

    Attributes:
        LARGEST: Select the largest values.
        SMALLEST: Select the smallest values.
    """

    LARGEST = enum.auto()
    SMALLEST = enum.auto()


class OptimizeObjective(enum.Enum):
    """Enum for optimization objectives.

    Attributes:
        MINIMIZE_RISK: Minimize risk.
        MAXIMIZE_RETURN: Maximize return.
        MAXIMIZE_UTILITY: Maximize utility (return minus risk).
        MAXIMIZE_RATIO: Maximize the ratio of return to risk.
    """

    MINIMIZE_RISK = ObjectiveFunction.MINIMIZE_RISK
    MAXIMIZE_RETURN = ObjectiveFunction.MAXIMIZE_RETURN
    MAXIMIZE_UTILITY = ObjectiveFunction.MAXIMIZE_UTILITY
    MAXIMIZE_RATIO = ObjectiveFunction.MAXIMIZE_RATIO


class RiskMetric(enum.Enum):
    """Enum for risk metrics.

    Attributes:
        VARIANCE: Variance
        SEMI_VARIANCE: Semi-variance
        STANDARD_DEVIATION: Standard deviation
        SEMI_DEVIATION: Semi-deviation
        MEAN_ABSOLUTE_DEVIATION: Mean absolute deviation
        CVAR: Conditional value at risk
        CDAR: Conditional drawdown at risk
        WORST_REALIZATION: Worst realization
        MAX_DRAWDOWN: Maximum drawdown
        AVERAGE_DRAWDOWN: Average drawdown
    """

    VARIANCE = RiskMeasure.VARIANCE
    SEMI_VARIANCE = RiskMeasure.SEMI_VARIANCE
    STANDARD_DEVIATION = RiskMeasure.STANDARD_DEVIATION
    SEMI_DEVIATION = RiskMeasure.SEMI_DEVIATION
    MEAN_ABSOLUTE_DEVIATION = RiskMeasure.MEAN_ABSOLUTE_DEVIATION
    CVAR = RiskMeasure.CVAR
    CDAR = RiskMeasure.CDAR
    WORST_REALIZATION = RiskMeasure.WORST_REALIZATION
    MAX_DRAWDOWN = RiskMeasure.MAX_DRAWDOWN
    AVERAGE_DRAWDOWN = RiskMeasure.AVERAGE_DRAWDOWN


class DataColumn(enum.Enum):
    """Enum for data columns.

    Attributes:
        OPEN: Open prices.
        HIGH: High prices.
        LOW: Low prices.
        CLOSE: Close prices.
        VOLUME: Volume data.
    """

    OPEN = enum.auto()
    HIGH = enum.auto()
    LOW = enum.auto()
    CLOSE = enum.auto()
    VOLUME = enum.auto()
