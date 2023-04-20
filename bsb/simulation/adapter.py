import abc


class SimulatorAdapter:
    def simulate(self, simulation):
        """
        Simulate the given simulation.
        """
        with simulation.scaffold.storage.read_only():
            data = self.prepare(simulation)
            for hook in simulation.post_prepare:
                hook(self, data)
            result = self.run(simulation)
            return self.collect(simulation, data, result)

    @abc.abstractmethod
    def prepare(self, simulation, comm=None):
        """
        Reset the simulation backend and prepare for the given simulation.

        :param simulation: The simulation configuration to prepare.
        :type simulation: ~bsb.simulation.simulation.Simulation
        :param comm: The MPI communicator to use. Only nodes in the communicator will
          participate in the simulation. The first node will idle as the main node. Calls
          :meth:`~bsb.simulation.adapter.SimulatorAdapter.set_communicator`
        """
        pass

    @abc.abstractmethod
    def run(self, simulation):
        """
        Fire up the prepared adapter.
        """
        pass

    @abc.abstractmethod
    def collect(self, simulation, simdata, simresult):
        """
        Collect the output of a simulation that completed
        """
        simresult.flush()
        return simresult

    @abc.abstractmethod
    def set_communicator(self, comm):
        """
        Set the communicator for this adapter.
        """
        pass
