from logging import info, debug
from time import time
from typing import List, Tuple

from numpy.random import default_rng


class Simulator:
    def __init__(self, lam, mi, servers: int, time_limit: float,
                 events_limit: int, seed: int):
        self.lam = lam  # Lambda
        self.mi = mi  # Mi
        self.servers = servers  # Number of servers
        self.time_limit = time_limit  # Max simulation time
        self.events_limit = events_limit  # Max number of events
        self.busy = 0  # Busy servers counter
        self.start_time = 0  # Simulation start time
        self.arrivals = 0  # Incoming packet counter
        self.blocked = 0  # Rejected packet counter
        self.served = 0  # Served packet counter
        self.event_list: List[Tuple] = []  # Event list
        self.rng = default_rng(seed)  # Random number generator
        self.blocking_probability = 0

    def end(self):
        """End simulation condition."""

        return (time() - self.start_time > self.time_limit) or \
               (self.arrivals >= self.events_limit)

    def run(self):
        """Run simulation."""

        info('Starting simulation')
        self.start_time = time()

        # Add primary event on list
        ev = ('arrival', self.start_time)
        self.event_list.append(ev)
        self.arrivals += 1
        debug(f'Adding to event list {ev}')

        while not self.end():
            # Take event from list
            ev = self.pop_list()
            ev_type, ev_time = ev
            debug(f'New event appeared {ev}')

            if ev_type == 'arrival':
                if not self.servers_busy():
                    eos_ev = (f'end_of_service_{self.busy + 1}',
                              ev_time + self.serve_time())
                    self.event_list.append(eos_ev)
                    self.busy += 1
                    debug(f'Adding to event list {eos_ev}')
                else:
                    self.blocked += 1

                new_ev = ('arrival', ev_time + self.arrival_time())
                self.event_list.append(new_ev)
                self.arrivals += 1
                debug(f'Adding to event list {new_ev}')

            elif 'end_of_service' in ev_type:
                self.served += 1
                self.busy -= 1

        self.blocking_probability = self.blocked / self.arrivals

        info(f'Results: '
             f'arrivals = {self.arrivals}, '
             f'served = {self.served}, '
             f'blocked = {self.blocked}, '
             f'P_block = {self.blocking_probability}')

    def pop_list(self):
        """Returns next to come event."""

        # Sort ascending by time
        self.event_list.sort(key=lambda x: x[1])
        # Take event with smallest time
        ev = self.event_list[0]
        # Remove it from list by overwriting list bypassing zero element
        self.event_list = self.event_list[1:]
        # Return the event
        return ev

    def serve_time(self):
        """Generate serving time."""

        # TODO: rozne rozklady prawd. (policzyc wartosc srednia np. lognormala)
        return self.rng.exponential(1 / self.mi)

    def arrival_time(self):
        """Generate arrival time."""

        return self.rng.exponential(1 / self.lam)

    def servers_busy(self):
        """Check if server is busy by comparing number of end_of_service
        events with number of servers. """

        return self.busy == self.servers

    def get_result(self):
        return self.blocking_probability
