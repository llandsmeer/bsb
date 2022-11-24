import abc
import types
import numpy as np
from ..reporting import report
from time import time
import itertools
from .. import config
from ._backends import get_simulation_nodes
from .cell import CellModel
from .connection import ConnectionModel
from .device import DeviceModel
from ..config import types as cfgtypes


class ProgressEvent:
    def __init__(self, progression, duration, time):
        self.progression = progression
        self.duration = duration
        self.time = time


@config.pluggable(key="simulator", plugin_name="simulation backend")
class Simulation:
    name = config.attr(key=True)
    duration = config.attr(type=float, required=True)
    cell_models = config.slot(type=CellModel, required=True)
    connection_models = config.slot(type=ConnectionModel, required=True)
    devices = config.slot(type=DeviceModel, required=True)
    post_prepare = config.list(type=cfgtypes.class_())

    @staticmethod
    def __plugins__():
        return get_simulation_nodes()

    @abc.abstractmethod
    def get_rank(self):
        """
        Return the rank of the current node.
        """
        pass

    @abc.abstractmethod
    def get_size(self):
        """
        Return the size of the collection of all distributed nodes.
        """
        pass

    @abc.abstractmethod
    def broadcast(self, data, root=0):
        """
        Broadcast data over MPI
        """
        pass

    def start_progress(self, duration):
        """
        Start a progress meter.
        """
        self._progdur = duration
        self._progstart = self._last_progtic = time()
        self._progtics = 0

    def progress(self, step):
        """
        Report simulation progress.
        """
        now = time()
        tic = now - self._last_progtic
        self._progtics += 1
        el = now - self._progstart
        report(
            f"Simulated {step}/{self._progdur}ms.",
            f"{el:.2f}s elapsed.",
            f"Simulated tick in {tic:.2f}.",
            f"Avg tick {el / self._progtics:.4f}s",
            level=3,
            ongoing=False,
        )
        progress = types.SimpleNamespace(
            progression=step, duration=self._progdur, time=time()
        )
        self._last_progtic = now
        return progress

    def step_progress(self, duration, step=1):
        steps = itertools.chain(np.arange(0, duration), (duration,))
        a, b = itertools.tee(steps)
        next(b, None)
        yield from zip(a, b)

    def add_progress_listener(self, listener):
        self._progress_listeners.append(listener)
