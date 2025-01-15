# pybacktestchain

Tool for creating, analyzing, and comparing backtesting strategies for financial portfolios. Stores backtest results securely on a blockchain. 

## **Features**
- **Backtest Multiple Strategies**: Includes Momentum, Mean Reversion, Equal Weight, and First Two Moments.
- **Customizable Settings**: Adjust rebalancing frequencies (daily, weekly, monthly) and define custom universes of assets.
- **Performance Metrics**: Evaluate portfolios with metrics like Annualized Returns, Volatility, Sharpe Ratio, and Max Drawdown.
- **User-Friendly CLI**:  Easily execute backtests through the command-line interface.
- **Extensible Framework**: Add new strategies, metrics, or features with minimal effort.
- **Secure Blockchain Storage**: Store and verify your backtests using blockchain technology.

## Installation

```bash
$ pip install pybacktestchain
```

## Usage

- Run backtest via CLI
- Add your custom strategy; extend the framework by:
    1. Creating a new class inheriting from {Information}.
    2. Implementing the {compute_portfolio} and {compute_information} methods.
    3. Registering your strategy in the CLI's {strategy_map}.

## Know Issues
- While the framework supports multiple strategies (e.g., Momentum, Mean Reversion), not all strategies produced valid backtest results.
- Data inconsistencies or edge cases in the portfolio allocation logic may be the reason behind.
- Future improvements could address these by debugging specific strategy implementation.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`pybacktestchain` was created by Juan F. Imbet. It is licensed under the terms of the MIT license.

## Credits

`pybacktestchain` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
