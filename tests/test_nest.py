from bsb.config import from_file
from bsb.core import Scaffold
from bsb.unittest import RandomStorageFixture, get_config_path
import numpy as np
import unittest


class TestNest(RandomStorageFixture, unittest.TestCase, engine_name="hdf5"):
    def test_gif_pop_psc_exp(self):
        """Mimics test_gif_pop_psc_exp of NEST's test suite to validate the adapter."""
        import nest

        pop_size = 500

        cfg = from_file(get_config_path("test_gif_pop_psc_exp.json"))
        ct = cfg.cell_types.gif_pop_psc_exp
        sim_cfg = cfg.simulations.test
        sim_cfg.resolution = 0.5
        sim_cfg.cell_models.gif_pop_psc_exp.constants["N"] = pop_size

        network = Scaffold(cfg, self.storage)
        network.compile()

        simdata = None
        simulation = None
        vm = None
        nspike = None

        def probe(adapter, sim, data):
            # Probe and steal some local refs to data that's otherwise encapsulated :)
            nonlocal simdata, vm, simulation
            simulation = sim
            simdata = data

            # Get the important information out of the sim/data
            cell_m = sim.cell_models.gif_pop_psc_exp
            conn_m = sim.connection_models.gif_pop_psc_exp
            pop = data.populations[cell_m]
            syn = data.connections[conn_m]

            # Add a voltmeter
            vm = nest.Create(
                "voltmeter",
                params={"record_from": ["n_events"], "interval": sim.resolution},
            )
            nest.Connect(vm, pop)

            # Add a spying recorder
            def spy(segment):
                nonlocal nspike

                start_time = 1000
                start_step = int(start_time / simulation.resolution)
                nspike = vm.events["n_events"][start_step:]

            data.result.create_recorder(spy)

            # Test node parameter transfer
            for param, value in {
                "V_reset": 0.0,
                "V_T_star": 10.0,
                "E_L": 0.0,
                "Delta_V": 2.0,
                "C_m": 250.0,
                "tau_m": 20.0,
                "t_ref": 4.0,
                "I_e": 500.0,
                "lambda_0": 10.0,
                "tau_syn_in": 2.0,
                "tau_sfa": (500.0,),
                "q_sfa": (1.0,),
            }.items():
                with self.subTest(param=param, value=value):
                    self.assertEqual(value, pop.get(param))

            # Test synapse parameter transfer
            for param, value in (("weight", -6.25), ("delay", 1)):
                with self.subTest(param=param, value=value):
                    self.assertEqual(value, syn.get(param))

        network.simulations.test.post_prepare.append(probe)
        network.run_simulation("test")

        mean_nspike = np.mean(nspike)
        mean_rate = mean_nspike / pop_size / simulation.resolution * 1000.0

        var_nspike = np.var(nspike)
        var_nspike = var_nspike / pop_size / simulation.resolution * 1000.0
        var_rate = var_nspike / pop_size / simulation.resolution * 1000.0

        err_mean = 1.0
        err_var = 6.0
        expected_rate = 22.0
        expected_var = 102.0

        self.assertGreaterEqual(err_mean, abs(mean_rate - expected_rate))
        self.assertGreaterEqual(err_var, var_rate - expected_var)
