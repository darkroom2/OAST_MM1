from itertools import product
from json import loads, JSONDecodeError, dumps
from logging import info
from multiprocessing import Pool
from pathlib import Path

from numpy import mean
from numpy.random import default_rng
from scipy.stats import t, sem

from simulator.simulator import Simulator
from simulator.utils import setup_logger, get_max_traffic


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

        mi_values = self.config.get('mi_values', [1])
        server_counts = self.config.get('server_counts', [5])
        target_probabilities = self.config.get('blocking_probabilities', [0.2])
        sim_repetitions = self.config.get('simulation_repetitions', 10)
        info('Simulation config loaded')

        info(f'Running simulator with k = {sim_repetitions} repetitions for '
             f'each combination of μ values, server counts and target '
             f'probabilities')
        with Pool() as pool:
            combinations = product(target_probabilities, mi_values,
                                   server_counts)
            self.results = pool.map(self.simulate, combinations)

        info(f'Results: {self.results}')
        Path(self.results_path).write_text(dumps(self.results))

    def simulate(self, combination):
        show_plots = self.config.get('show_plots', True)
        sim_repetitions = self.config.get('simulation_repetitions', 10)
        time_limit = self.config.get('time_limit', 10)
        events_limit = self.config.get('events_limit', 10000)

        target_probability, mi, servers = combination

        target_rho = get_max_traffic(target_probability, servers,
                                     show_plot=show_plots)
        info(f'Max traffic ϱ = {target_rho}, for N = {servers} servers and '
             f'P_block = {target_probability}')

        lam = mi * target_rho
        info(f'Calculated λ = {lam} for μ = {mi}')

        simulator_results = {
            'servers': servers,
            'target_probability': target_probability,
            'target_rho': target_rho,
            'mi': mi,
            'lam': lam
        }
        simulated_probabilities = []
        for i in range(sim_repetitions):
            info(f'Running #{i + 1} simulation')
            sim = Simulator(lam=lam, mi=mi, servers=servers,
                            time_limit=time_limit,
                            events_limit=events_limit,
                            seed=self.rng.integers(999999))
            sim.run()

            sim_prob = sim.get_result()
            info(f'Simulated P_block = {sim_prob}')

            simulated_probabilities.append(sim_prob)
        simulator_results['simulated_probabilities'] = simulated_probabilities

        confidence_interval = t.interval(alpha=0.95,
                                         df=len(simulated_probabilities) - 1,
                                         loc=mean(simulated_probabilities),
                                         scale=sem(simulated_probabilities))

        simulator_results['confidence_interval'] = confidence_interval
        return simulator_results

    def get_rng(self):
        seed = self.config.get('seed', 123)
        return default_rng(seed)

    def get_results(self):
        return self.results

    def show_results(self):
        results = self.results
        if not results:
            results = self.load_json(self.results_path)

        fix_servers_fix_prob = [
            result for result in results if
            result['servers'] == 9 and result['target_probability'] == 0.2
        ]

        fix_servers_fix_mi = [
            result for result in results if
            result['servers'] == 9 and result['mi'] == 0.4
        ]

        fix_prob_fix_mi = [
            result for result in results if
            result['target_probability'] == 0.2 and result['mi'] == 1
        ]


def main():
    """Testing simulator."""

    logger = setup_logger()

    logger.info('Starting simulation')

    sim = Simulation('config/config.json', 'results.json')
    sim.run()
    # sim.show_results()


if __name__ == '__main__':
    main()
