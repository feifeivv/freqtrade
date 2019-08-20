"""
This module contains the argument manager class
"""
import argparse
from typing import List, Optional

from freqtrade.configuration.cli_options import AVAILABLE_CLI_OPTIONS
from freqtrade import constants

ARGS_COMMON = ["verbosity", "logfile", "version", "config", "datadir"]

ARGS_STRATEGY = ["strategy", "strategy_path"]

ARGS_MAIN = ARGS_COMMON + ARGS_STRATEGY + ["db_url", "sd_notify"]

ARGS_COMMON_OPTIMIZE = ["ticker_interval", "timerange",
                        "max_open_trades", "stake_amount", "refresh_pairs"]

ARGS_BACKTEST = ARGS_COMMON_OPTIMIZE + ["position_stacking", "use_max_market_positions",
                                        "live", "strategy_list", "export", "exportfilename"]

ARGS_HYPEROPT = ARGS_COMMON_OPTIMIZE + ["hyperopt", "hyperopt_path",
                                        "position_stacking", "epochs", "spaces",
                                        "use_max_market_positions", "print_all",
                                        "print_colorized", "print_json", "hyperopt_jobs",
                                        "hyperopt_random_state", "hyperopt_min_trades",
                                        "hyperopt_continue", "hyperopt_loss"]

ARGS_EDGE = ARGS_COMMON_OPTIMIZE + ["stoploss_range"]

ARGS_LIST_EXCHANGES = ["print_one_column"]

ARGS_DOWNLOADER = ARGS_COMMON + ["pairs", "pairs_file", "days", "exchange", "timeframes", "erase"]

ARGS_PLOT_DATAFRAME = (ARGS_COMMON + ARGS_STRATEGY +
                       ["pairs", "indicators1", "indicators2", "plot_limit", "db_url",
                        "trade_source", "export", "exportfilename", "timerange",
                        "refresh_pairs", "live"])

ARGS_PLOT_PROFIT = (ARGS_COMMON + ARGS_STRATEGY +
                    ["pairs", "timerange", "export", "exportfilename", "db_url", "trade_source"])


class Arguments(object):
    """
    Arguments Class. Manage the arguments received by the cli
    """
    def __init__(self, args: Optional[List[str]], description: str,
                 no_default_config: bool = False) -> None:
        self.args = args
        self._parsed_arg: Optional[argparse.Namespace] = None
        self.parser = argparse.ArgumentParser(description=description)
        self._no_default_config = no_default_config

    def _load_args(self) -> None:
        self._build_args(optionlist=ARGS_MAIN)
        self._build_subcommands()

    def get_parsed_arg(self) -> argparse.Namespace:
        """
        Return the list of arguments
        :return: List[str] List of arguments
        """
        if self._parsed_arg is None:
            self._load_args()
            self._parsed_arg = self._parse_args()

        return self._parsed_arg

    def _parse_args(self) -> argparse.Namespace:
        """
        Parses given arguments and returns an argparse Namespace instance.
        """
        parsed_arg = self.parser.parse_args(self.args)

        # Workaround issue in argparse with action='append' and default value
        # (see https://bugs.python.org/issue16399)
        if not self._no_default_config and parsed_arg.config is None:
            parsed_arg.config = [constants.DEFAULT_CONFIG]

        return parsed_arg

    def _build_args(self, optionlist, parser=None):
        parser = parser or self.parser

        for val in optionlist:
            opt = AVAILABLE_CLI_OPTIONS[val]
            parser.add_argument(*opt.cli, dest=val, **opt.kwargs)

    def _build_subcommands(self) -> None:
        """
        Builds and attaches all subcommands.
        :return: None
        """
        from freqtrade.optimize import start_backtesting, start_hyperopt, start_edge
        from freqtrade.utils import start_list_exchanges

        subparsers = self.parser.add_subparsers(dest='subparser')

        # Add backtesting subcommand
        backtesting_cmd = subparsers.add_parser('backtesting', help='Backtesting module.')
        backtesting_cmd.set_defaults(func=start_backtesting)
        self._build_args(optionlist=ARGS_BACKTEST, parser=backtesting_cmd)

        # Add edge subcommand
        edge_cmd = subparsers.add_parser('edge', help='Edge module.')
        edge_cmd.set_defaults(func=start_edge)
        self._build_args(optionlist=ARGS_EDGE, parser=edge_cmd)

        # Add hyperopt subcommand
        hyperopt_cmd = subparsers.add_parser('hyperopt', help='Hyperopt module.')
        hyperopt_cmd.set_defaults(func=start_hyperopt)
        self._build_args(optionlist=ARGS_HYPEROPT, parser=hyperopt_cmd)

        # Add list-exchanges subcommand
        list_exchanges_cmd = subparsers.add_parser(
            'list-exchanges',
            help='Print available exchanges.'
        )
        list_exchanges_cmd.set_defaults(func=start_list_exchanges)
        self._build_args(optionlist=ARGS_LIST_EXCHANGES, parser=list_exchanges_cmd)