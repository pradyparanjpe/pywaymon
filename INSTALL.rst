***************
Prerequisites
***************

- `gcc <https://gcc.gnu.org/>`__
- Python3
- pip
- `lmsensors <https://github.com/lm-sensors/lm-sensors>`__

********
Install
********

pip
====
Preferred method

Install
--------

.. tabs::

    .. tab:: pip

       .. code-block:: sh
          :caption: install

          pip install git+https://gitlab.com/pradyparanjpe/pywaymon.git


    .. tab:: module import

       .. code-block:: sh
          :caption: if ``command not found: pip``

          python3 -m pip install git+https://gitlab.com/pradyparanjpe/pywaymon.git


Update
-------

.. tabs:: 

    .. tab:: pip

       .. code-block:: sh
          :caption: install

          pip install -U git+https://gitlab.com/pradyparanjpe/pywaymon.git


    .. tab:: module import

       .. code-block:: sh
          :caption: if ``command not found: pip``

          python3 -m pip install -U git+https://gitlab.com/pradyparanjpe/pywaymon.git


Uninstall
----------

.. tabs::

    .. tab:: pip

       .. code-block:: sh
          :caption: uninstall

          pip uninstall pywaymon


    .. tab:: module import

       .. code-block:: sh
          :caption: if ``command not found: pip``

          python3 -m pip uninstall pywaymon


Cloned
=======
*(Nightly)*

Requirements
--------------
*(Additional,) Only for this installation method.*

- `git <https://git-scm.com/>`__

Pull
-----
.. code-block:: sh

      git pull https://gitlab.com/pradyparanjpe/pywaymon.git && cd pywaymon


Install
--------

.. tabs::

    .. tab:: pip

       .. code-block:: sh
          :caption: install

          pip install .


    .. tab:: module import

       .. code-block:: sh
          :caption: if ``command not found: pip``

          python3 -m pip install .
