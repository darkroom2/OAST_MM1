from logging import getLogger, INFO, Formatter, StreamHandler, FileHandler
from math import factorial

import matplotlib.pyplot as plt
from numpy import arange, abs as np_abs


def setup_logger(level=INFO):
    """Configures logger with preset format."""

    _logger = getLogger()
    _logger.setLevel(level)

    formatter = Formatter(
        '%(asctime)s %(processName)s %(threadName)s - %(levelname)s - %('
        'message)s '
    )

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    file_handler = FileHandler('simulation.log')
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


def erlang_b(traffic, servers):
    """Erlang's B formula. Used for dimensioning different types of networks."""

    numerator = traffic ** servers / factorial(servers)
    _sum = 0
    for i in range(0, servers + 1):
        _sum += (traffic ** i) / factorial(i)
    return numerator / _sum


def get_max_traffic(target_prob, servers, max_erlangs=500, accuracy=0.0001,
                    show_plot=False):
    """Find value of max traffic offered to the system for given loss
    probability and number of serving devices."""

    erlangs = arange(0, max_erlangs, accuracy)
    probabilities = erlang_b(erlangs, servers)

    traffic = get_x_for_y(x=erlangs, y=probabilities, value=target_prob)
    (x, y) = (traffic, target_prob)

    if show_plot:
        plt.title(f'Erlang B formula for N = {servers} servers and '
                  f'$P_b$ = {target_prob}')
        plt.plot(erlangs, probabilities)
        plt.xlabel('traffic ϱ [Erlangs]')
        plt.ylabel('blocking probability')
        plt.plot(x, y, 'ro')
        plt.text(x + 10, y, f'({x}, {y})')
        plt.show()

    return traffic


def find_closest(array, value):
    """Returns the index of the value closest to the specified value among
    the array. """

    return np_abs(array - value).argmin()


def get_x_for_y(x, y, value):
    """Returns the corresponding value from array Y for the value from array
    X that is closest to the specified value. """

    idx = find_closest(y, value)
    return x[idx]
