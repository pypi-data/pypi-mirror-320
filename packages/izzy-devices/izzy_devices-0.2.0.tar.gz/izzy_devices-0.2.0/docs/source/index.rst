izzy-devices documentation
==========================

.. include:: ../../README.md
   :start-line: 23
   :end-line: 30

.. note::
    When instantiated in software on an IZZY device, a ``server`` instance should not be used to hold a list of
    ``client`` devices as remote devices should not communicate to each other. A ``server`` instance on an IZZY device
    should only be used to store network information about the Mother device.

.. include:: ../../README.md
   :start-line: 36
   :end-line: 38

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. contents::
   :local:

Client
******
.. automodule:: client
   :members:

Server
******
.. automodule:: server
   :members:

Client Statuses
***************
.. automodule:: client_status
   :members:

Server Statuses
***************
.. automodule:: server_status
   :members:


