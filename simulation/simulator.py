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
        self.queued = 0  # Queue length counter
        self.served = 0  # Served packet counter
        self.event_list: List[Tuple] = []  # Event list
        self.rng = default_rng(seed)  # Random number generator
        self.blocking_probability = 0

    def end(self):
        """End simulation condition."""

        return ((time() - self.start_time) > self.time_limit) or \
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
                    # TODO: SPRAWDZIC CZY SIE NIE JEBIE TU PRZY UZYCIU
                    #  last_end_of_service_time(), latwiej bedzie bez
                    #  multiprocessingu i poola...
                    wait_ev = (f'waiting_{self.queued + 1}',
                               self.earliest_eos_time())
                    self.event_list.append(wait_ev)
                    self.queued += 1
                    debug(f'Adding to event list {wait_ev}')

                new_ev = ('arrival', ev_time + self.arrival_time())
                self.event_list.append(new_ev)
                self.arrivals += 1
                debug(f'Adding to event list {new_ev}')

            elif 'waiting' in ev_type:
                if not self.servers_busy():
                    eos_ev = (f'end_of_service_{self.busy + 1}',
                              ev_time + self.serve_time())
                    self.event_list.append(eos_ev)
                    self.busy += 1
                    self.queued -= 1
                    debug(f'Adding to event list {eos_ev}')
                else:
                    wait_ev = (f'{ev_type}', self.earliest_eos_time())
                    self.event_list.append(wait_ev)
                    debug(f'Updating in event list {wait_ev}')

            elif 'end_of_service' in ev_type:
                self.served += 1
                self.busy -= 1
                debug(f'{ev_type}: Incrementing served, decrementing busy')

        # TODO: statystyki z githuba podjebac KAROLINAAAAA
        self.blocking_probability = self.queued / self.arrivals

        info(f'Results: '
             f'arrivals = {self.arrivals}, '
             f'served = {self.served}, '
             f'queued = {self.queued}, '
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
        events with number of servers. """

        return self.busy == self.servers

    def get_result(self):
        return self.blocking_probability
