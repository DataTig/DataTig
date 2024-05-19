CLI
===

Call
----

Call via Python:

.. code-block:: bash

    python -m datatig.cli --help

Build sub-command
-----------------

This takes a site and builds some outputs for you.

Call with the directory of the data and at least one of these options:

* `--staticsiteoutput` - A directory in which the files of the static site will be placed. This can already exist.
* `--sqliteoutput` - A location at which a SQL database file will be placed. This should not already exist.
* `--frictionlessoutput` - A location at which a Frictionless Data Zip file will be placed. This should not already exist.

.. code-block:: bash

    python -m datatig.cli build . --staticsiteoutput _site --sqliteoutput database.sqlite


Any build errors will be printed to screen. (Data validation errors will not be) If encountered, the process will try to continue ignoring the problem. The exit code of the process will be 0 if a success, or -1 if there were any errors. This means you can use this as part of a C.I./C.D. pipeline and check the response.

If you select static site, you can also pass:

* `--staticsiteurl` - Base URL that resulting website will be hosted at. Should not have a trailing slash. eg 'http://www.example.com/sub-directory'

Check sub-command
-----------------

This takes a site and checks it for you.

Call with the directory of the data.

Any build errors or data validation errors will be printed to screen.

The exit code of the process will be 0 if a success, or -1 if there were any errors. This means you can use this as part of a C.I./C.D. pipeline and check the response.

.. code-block:: bash

    python -m datatig.cli check .

Versioned Build sub-command
---------------------------

This is currently used for internal testing and is not documented

.. _reference_cli_local_servers:

Local Server feature
--------------------

Call with the directory of the data.

.. code-block:: bash

    python -m datatig.localserver.run .

Part of the output will be a URL address - open this in your webbrowser.

(Note: :doc:`For an explanation of this feature, see here. <../explanation/local-server>` )

