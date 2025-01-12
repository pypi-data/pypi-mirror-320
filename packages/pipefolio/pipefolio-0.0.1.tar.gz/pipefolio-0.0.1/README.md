# Pipefolio: A Pipeline-Oriented Portfolio Optimization Framework

![logo](https://raw.githubusercontent.com/kfuangsung/pipefolio/refs/heads/main/docs/_static/pipefolio-logo.png)
    
## About the project

**Pipefolio** is a Python-based portfolio optimization framework designed with a pipeline-oriented approach. While several excellent Python libraries for portfolio optimization already exist—such as [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt), [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib), and [skfolio](https://github.com/skfolio/skfolio)—Pipefolio takes a different direction.

Built on top of [scikit-learn](https://scikit-learn.org/stable/), Pipefolio leverages existing optimization algorithms while minimizing boilerplate code through the use of the **pipe (`|`) operator**, enabling a streamlined and efficient workflow.

The framework provides the following types of models, each serving a specific purpose in the portfolio optimization process:

* **Selector**<br>
Screens assets to narrow down the investment universe.

* **Transformer**<br>
Transforms and preprocesses data to ensure compatibility with optimization models.

* **Optimizer**<br>
Implements portfolio optimization algorithms to generate optimal allocations.

* **Adaptor**<br>
Extracts and formats the optimized weights for further analysis or implementation.

## Getting started

### Installation

```bash
pip install pipefolio
```

### [Documentation](https://kfuangsung.github.io/pipefolio)

## Usages

This example download stock data using [yfinance](https://github.com/ranaroussi/yfinance).


```python
import yfinance as yf
from pipefolio.adaptor import WeightMappingAdaptor, WeightArrayAdaptor
from pipefolio.data import DataPlaceHolder
from pipefolio.enums import RiskMetric, SelectMode
from pipefolio.optimizer import (
    EqualWeightOptimizer,
    InverseVolatilityOptimizer,
    RiskAverseOptimizer,
)
from pipefolio.selector import (
    AnnualVolatilitySelector,
    AverageTradeValueSelector,
    TotalReturnSelector,
)
from pipefolio.transformer import PriceToReturnTransformer

# download data via yfinance
data = yf.download(
    ["AAPL", "AMZN", "NVDA", "BRK-B", "KO", "JNJ", "TSLA", "GS", "WMT", "MCD"],
    period="1y",
    interval="1d",
)

# data must be wrapped by DataPlaceHolder
data = DataPlaceHolder.from_dataframe(data)

# pipeline -> return optimized weights
(
    data
    | AverageTradeValueSelector(5)  # selector
    | PriceToReturnTransformer()  # transformer
    | InverseVolatilityOptimizer()  # optimizer
    | WeightMappingAdaptor()  # adaptor
)
# {'NVDA': np.float64(0.10316247719888795),
#  'TSLA': np.float64(0.08487498757904818),
#  'AAPL': np.float64(0.24167068511508258),
#  'AMZN': np.float64(0.19489272842965072),
#  'BRK-B': np.float64(0.3753991216773305)}


# chaining multiple selectors
(
    data
    | AverageTradeValueSelector(8, SelectMode.LARGEST)
    | TotalReturnSelector(5, SelectMode.LARGEST)
    | AnnualVolatilitySelector(3, SelectMode.SMALLEST)
    | PriceToReturnTransformer()
    | EqualWeightOptimizer()
    | WeightMappingAdaptor()
)
# {'WMT': np.float64(0.3333333333333333),
#  'GS': np.float64(0.3333333333333333),
#  'AMZN': np.float64(0.3333333333333333)}


# with different adaptor
(
    data
    | PriceToReturnTransformer()
    | RiskAverseOptimizer(RiskMetric.STANDARD_DEVIATION, risk_aversion=2)
    | WeightArrayAdaptor()
)
# array([6.38077192e-02, 1.94597392e-02, 1.59637665e-01, 9.15442233e-03,
#        1.94553086e-01, 2.87905182e-01, 3.25055500e-02, 6.43214713e-02,
#        2.21196278e-09, 1.68655163e-01])
```

### Supported Models

* **Selector**
    * `AnnualVolatilitySelector`
    * `AverageTradeValueSelector`
    * `TotalReturnSelector`
* **Transformer**
    * `PriceToReturnTransformer`
* **Optimizer**
    * `EqualWeightOptimizer`
    * `InverseVolatilityOptimizer`
    * `MaxRatioOptimizer`
    * `MaxReturnOptimizer`
    * `MinRiskOptimizer`
    * `RiskAverseOptimizer`
* **Adaptor**
    * `WeightArrayAdaptor`
    * `WeightMappingAdaptor`

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/kfuangsung/pipefolio/blob/main/LICENSE) for more information.

## Maintainers

[pipefolio](https://github.com/kfuangsung/pipefolio) is currently maintained by [kfuangsung](https://github.com/kfuangsung) (kachain.f@outlook.com).

## Acknowledgments

* [skfolio](https://github.com/skfolio/skfolio): Python library for portfolio optimization built on top of scikit-learn.
* [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt): Financial portfolio optimisation in python, including classical efficient frontier, Black-Litterman, Hierarchical Risk Parity.
* [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib): Portfolio Optimization and Quantitative Strategic Asset Allocation in Python.