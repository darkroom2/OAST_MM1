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
        self.arrivals = 0  # Incoming clients counter
        self.queued = 0  # Queue length counter
        self.served = 0  # Served clients counter
        self.event_list: List[Tuple] = []  # Event list
        self.history_list: List[Tuple] = []  # Historical event list
        self.rng = default_rng(seed)  # Random number generator
        self.results = {}  # Dict with statistics for each event

    def end(self):
        """End simulation condition."""

        return ((time() - self.start_time) > self.time_limit) or \
               (self.served >= self.events_limit)

    def run(self):
        """Run simulation."""

        debug('Starting simulation')
        self.start_time = time()

        # Add primary event on list
        self.arrivals += 1
        ev = ('arrival', self.start_time, self.arrivals)
        self.event_list.append(ev)
        debug(f'Adding to event list {ev}')

        while not self.end():
            # Take event from list
            ev = self.pop_list()
            ev_type, ev_time, ev_id = ev
            debug(f'New event appeared {ev}')

            if ev_type == 'arrival':
                if not self.servers_busy():
                    self.busy += 1
                    eos_ev = (f'end_of_service', ev_time + self.serve_time(),
                              ev_id)
                    self.event_list.append(eos_ev)
                    debug(f'Adding to event list {eos_ev}')
                else:
                    self.queued += 1
                    wait_ev = (f'waiting', self.earliest_eos_time(), ev_id)
                    self.event_list.append(wait_ev)
                    debug(f'Adding to event list {wait_ev}')

                self.arrivals += 1
                new_ev = ('arrival', ev_time + self.arrival_time(),
                          self.arrivals)
                self.event_list.append(new_ev)
                debug(f'Adding to event list {new_ev}')

            elif 'waiting' in ev_type:
                if not self.servers_busy():
                    self.busy += 1
                    self.queued -= 1
                    eos_ev = (f'end_of_service', ev_time + self.serve_time(),
                              ev_id)
                    self.event_list.append(eos_ev)
                    debug(f'Adding to event list {eos_ev}')
                else:
                    wait_ev = (f'{ev_type}', self.earliest_eos_time(), ev_id)
                    self.event_list.append(wait_ev)
                    debug(f'Updating in event list {wait_ev}')

            elif 'end_of_service' in ev_type:
                self.served += 1
                self.busy -= 1
                debug(f'{ev_type}: Incrementing served, decrementing busy')

        debug('Simulation done')

    def pop_list(self):
        """Returns next to come event."""

        # Sort ascending by time
        self.event_list.sort(key=lambda x: x[1])
        # Take event with smallest time
        ev = self.event_list[0]
        # Remove it from list by overwriting list bypassing zero element
        self.event_list = self.event_list[1:]

        # Statistics update
        if self.results.get(ev[2], False):
            self.results[ev[2]].append(ev)
        else:
            self.results[ev[2]] = [ev]

        # Return the event
        return ev

    def earliest_eos_time(self):
        """Returns time of earliest end_of_service event."""

        # Filter all end_of_service events
        eos_events = list(
            filter(
                lambda x: 'end_of_service' in x[0], self.event_list
            )
        )
        # Sort ascending by time
        eos_events.sort(key=lambda x: x[1])
        # Take eos event with earliest time and return its time
        return eos_events[0][1]

    def serve_time(self):
        """Generate serving time."""

        return self.rng.exponential(1 / self.mi)

    def arrival_time(self):
        """Generate arrival time."""

        return self.rng.exponential(1 / self.lam)

    def servers_busy(self):
        """Check if server is busy by comparing number of end_of_service
        events with number of servers."""

        return self.busy == self.servers

    def get_result(self):
        # TODO: zrobic zeby dalo sie liczyc przedzialy ufnosci i srednia z K symulacji roznych parametrow
        return self.history_list
