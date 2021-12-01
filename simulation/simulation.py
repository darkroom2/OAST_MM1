from itertools import product
from json import loads, JSONDecodeError, dumps
from logging import info, DEBUG
from multiprocessing import Pool
from pathlib import Path

from numpy import mean
from numpy.random import default_rng
from scipy.stats import t, sem

from simulation.simulator import Simulator
from simulation.utils import setup_logger, get_max_traffic


class Simulation:
    def __init__(self, config_path, results_path):
        self.config_path = config_path
        self.results_path = results_path
        self.config = self.load_json(config_path)
        self.rng = self.get_rng()
        self.results = None

    @staticmethod
    def load_json(path):
        """Parse json file to dict."""

        config_file = Path(path)
        try:
            return loads(config_file.read_text(encoding='utf8'))
        except JSONDecodeError:
            return {}

    def run(self):

        # TODO: Wykresy zależności że np. P_block nie zmienia sie liniowo ze
        #  wzrostem serwerow itp. ze wynik jest niezalezny od roznych rozkladow
        #  czasu obslugi

        mi_values = self.config.get('mi_values', [0.6])
        lam_values = self.config.get('lam_values', [1])
        server_counts = self.config.get('server_counts', [1])
        sim_repetitions = self.config.get('simulation_repetitions', 10)
        info('Simulation config loaded')

        info(f'Running simulator with k = {sim_repetitions} repetitions for '
             f'each combination of μ, λ and server count values')
        combinations = product(mi_values, lam_values, server_counts)
        self.results = [
            self.simulate(combination) for combination in combinations
        ]

        info(f'Results: {self.results}')
        Path(self.results_path).write_text(dumps(self.results))

    def simulate(self, combination):
        show_plots = self.config.get('show_plots', True)
        sim_repetitions = self.config.get('simulation_repetitions', 10)
        time_limit = self.config.get('time_limit', 10)
        events_limit = self.config.get('events_limit', 10000)

        mi, lam, servers = combination

        rho = lam / mi
        info(f'λ = {lam}, μ = {mi} ==> ϱ = {rho}')

        simulation_results = {
            'mi': mi,
            'lam': lam,
            'rho': rho
        }

        simulator_results = []
        for i in range(sim_repetitions):
            info(f'Running #{i + 1} simulation')
            sim = Simulator(lam=lam, mi=mi, servers=servers,
                            time_limit=time_limit, events_limit=events_limit,
                            seed=self.rng.integers(999999))
            sim.run()

            sim_res = sim.get_result()
            info(f'Simulated results = {sim_res}')

            simulator_results.append(sim_res)
        simulation_results['simulator_results'] = simulator_results

        confidence_intervals = {
            alpha: t.interval(alpha=alpha, df=len(simulator_results) - 1,
                              loc=mean(simulator_results),
                              scale=sem(simulator_results))
            for alpha in [0.95, 0.99]
        }

        simulation_results['confidence_intervals'] = confidence_intervals
        return simulation_results

    def get_rng(self):
        seed = self.config.get('seed', 123)
        return default_rng(seed)

    def get_results(self):
        return self.results

    def show_results(self):
        results = self.results
        if not results:
            results = self.load_json(self.results_path)

        # fix_servers_fix_prob = [
        #     result for result in results if
        #     result['servers'] == 9 and result['target_probability'] == 0.2
        # ]
        #
        # fix_servers_fix_mi = [
        #     result for result in results if
        #     result['servers'] == 9 and result['mi'] == 0.4
        # ]
        #
        # fix_prob_fix_mi = [
        #     result for result in results if
        #     result['target_probability'] == 0.2 and result['mi'] == 1
        # ]


def main():
    """Testing simulation."""

    logger = setup_logger(level=DEBUG)

    logger.info('Starting simulation')

    sim = Simulation('config/config.json', 'results.json')
    sim.run()
    sim.show_results()


if __name__ == '__main__':
    main()
