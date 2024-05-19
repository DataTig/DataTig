Local Server
============

When you have some data checked out on your local machine, this feature allows you to view and edit data directly in your web browser.
Any changes you make are written to your local machine for you to commit to git and push up to a remote host.

It does this by running a web server on your machine, and letting you use a normal web browser to access this.

There is no security on this service; anyone who can access it can edit the data.
This means it is not suitable for running on an internet server.

To use it, you must install DataTig with the optional "localserver" extras.

.. code-block:: bash

   pip install datatig[localserver]

See:

*  How to run :ref:`reference_cli_local_servers`.


