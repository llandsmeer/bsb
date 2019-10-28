import unittest, os, sys, numpy as np, h5py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scaffold import Scaffold
from scaffold.config import JSONConfig
from scaffold.simulators.nest import NestCell
from scaffold.models import Layer, CellType

class TestSingleNeuronTypeSetup(unittest.TestCase):

    def setUp(self):
        config = JSONConfig(file="test_single_neuron.json")
        self.scaffold = Scaffold(config)
        self.scaffold.compile_network()
        self.nest_adapter = self.scaffold.configuration.simulations['test_single_neuron']


    def test_single_neuron(self):
        self.scaffold.run_simulation("test_single_neuron")
        test_cell_model = self.nest_adapter.cell_models["test_cell"]
        self.assertEqual(test_cell_model.identifiers, list(range(1,5)))
        # Parameters
        test_neuron_status = self.nest_adapter.nest.GetStatus(test_cell_model.identifiers)
        self.assertEqual(test_neuron_status[0]['t_ref'], 1.5)
        self.assertEqual(test_neuron_status[0]['C_m'], 7.0)
        self.assertEqual(test_neuron_status[0]['V_th'], -41.0)
        self.assertEqual(test_neuron_status[0]['V_reset'], -70.0)
        self.assertEqual(test_neuron_status[0]['E_L'], -62.0)
        self.assertEqual(test_neuron_status[0]['I_e'], 0.0)


class TestDoubleNeuronTypeSetup(unittest.TestCase):

    def setUp(self):
        config = JSONConfig(file="test_double_neuron.json")
        self.scaffold = Scaffold(config)
        self.scaffold.compile_network()
        self.nest_adapter = self.scaffold.configuration.simulations['test_double_neuron']

    def test_double_neuron(self):
        self.scaffold.run_simulation("test_double_neuron")
        test_cell_model = self.nest_adapter.cell_models["from_cell"]
        self.assertEqual(test_cell_model.identifiers, [1, 2, 3, 4])
        # Parameters IAF
        test_neuron_status = self.nest_adapter.nest.GetStatus(test_cell_model.identifiers)
        self.assertEqual(test_neuron_status[0]['t_ref'], 1.5)
        self.assertEqual(test_neuron_status[0]['C_m'], 7.0)
        self.assertEqual(test_neuron_status[0]['V_th'], -41.0)
        self.assertEqual(test_neuron_status[0]['V_reset'], -70.0)
        self.assertEqual(test_neuron_status[0]['E_L'], -62.0)
        self.assertEqual(test_neuron_status[0]['I_e'], 0.0)

        test_cell_model = self.nest_adapter.cell_models["to_cell"]
        self.assertEqual(test_cell_model.identifiers, [5, 6, 7, 8])
        # Parameters EGLIF
        test_neuron_status = self.nest_adapter.nest.GetStatus(test_cell_model.identifiers)
        self.assertEqual(test_neuron_status[0]['t_ref'], 1.5)
        self.assertEqual(test_neuron_status[0]['C_m'], 7.0)
        self.assertEqual(test_neuron_status[0]['Vth_init'], -41.0)
        self.assertEqual(test_neuron_status[0]['V_reset'], -70.0)
        self.assertEqual(test_neuron_status[0]['E_L'], -62.0)
        self.assertEqual(test_neuron_status[0]['Ie_const'], -0.888)
        self.assertEqual(test_neuron_status[0]['Vinit'], -62.0)
        self.assertEqual(test_neuron_status[0]['lambda_0'], 1.0)
        self.assertEqual(test_neuron_status[0]['delta_V'], 0.3)
        self.assertEqual(test_neuron_status[0]['Ie_const'], -0.888)
        self.assertEqual(test_neuron_status[0]['adaptC'], 0.022)
        self.assertEqual(test_neuron_status[0]['k1'], 0.311)
        self.assertEqual(test_neuron_status[0]['k2'], 0.041)
        self.assertEqual(test_neuron_status[0]['A1'], 0.01)
        self.assertEqual(test_neuron_status[0]['A2'], -0.94)


class TestDoubleNeuronNetworkSetup(unittest.TestCase):

    def setUp(self):
        config = JSONConfig(file="test_double_neuron_network.json")
        self.scaffold = Scaffold(config)
        self.scaffold.compile_network()
        self.nest_adapter = self.scaffold.configuration.simulations['test_double_neuron_network_static']

    def test_double_neuron_network(self):
        self.scaffold.run_simulation("test_double_neuron_network_static")
