==================
Installation Guide
==================


.. tip::

  Use virtual environments!

The scaffold framework can be installed using ``pip``:

.. code-block:: bash

  pip install "bsb>=4.0.0a0"

You can verify that the installation works with:

.. code-block:: python

  from bsb.core import Scaffold

  # Create an empty scaffold network with the default configuration.
  scaffold = Scaffold()

You can now head over to the :doc:`get started <getting-started>`.

Parallel support
================

The BSB parallelizes the network reconstruction using MPI, and translates simulator
instructions to the simulator backends with it as well, for effortless parallel
simulation. To use MPI from Python the `mpi4py
<https://mpi4py.readthedocs.io/en/stable/>`_ package is required, which in turn needs a
working MPI implementation installed in your environment.

On your local machine you can install OpenMPI:

.. code-block:: bash

  sudo apt-get update && sudo apt-get install -y libopenmpi-dev openmpi-bin

On Windows, install `Microsoft MPI
<https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi>`_. On
supercomputers it is usually installed already, otherwise contact your administrator.

To then install the BSB with MPI support:

.. code-block:: bash

  pip install "bsb[mpi]>=4.0.0a0"

Simulator backends
==================

If you'd like to install the scaffold builder for point neuron simulations with
NEST or multicompartmental neuron simulations with NEURON use:

.. code-block:: bash

  pip install bsb[nest]
  # or
  pip install bsb[neuron]
  # or both
  pip install bsb[nest,neuron]

.. note::

  This does not install the simulators themselves. It installs the Python tools that the
  BSB needs to deal with them. Install the simulators separately according to their
  respective installation instructions.

Installing NEST
===============

The BSB currently runs a fork of NEST 2.18. To install it, follow the instructions,
with a virtual environment activated.

.. code-block:: bash

  sudo apt-get update && apt-get install -y openmpi-bin libopenmpi-dev
  git clone https://github.com/dbbs-lab/nest-simulator
  cd nest-simulator
  mkdir build
  cd build
  pip install cmake cython
  cmake .. \
    -Dwith-mpi=ON \
    -Dwith-python=ON
  make install

Confirm your installation with:

.. code-block:: bash

  python -c "import nest; nest.test()"

.. note::

  There might be a few failed tests related to ``NEST_DATA_PATH`` but this is OK.
