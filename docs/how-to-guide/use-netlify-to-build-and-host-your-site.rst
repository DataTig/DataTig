Use Netlify to build and host your site
=======================================

Scenario
--------

You currently have a DataTig site in a Git repository.

You want to make sure the data is correct, at all times and when someone makes a pull request.

You can set up GitHub Actions to check this for you.

Steps
-----

In the top level of the repository, create a file `netlify.toml`. It's contents should be:

.. code-block:: toml

    [build]
      publish = "out"
      command = "pip install datatig && export PYTHONPATH=$(pwd) && python -m datatig build . --staticsiteoutput out"

In the top level of the repository, create a file `runtime.txt`. It's contents should be:

.. code-block:: text

    3.9

This should be a single line, with no extra spaces. It tells Netlify which version of Python to use.

Commit your files `netlify.toml` and `runtime.txt`. Merge them into your default branch (`main`, or whatever you use).

In Netlify, you should now be able to add the site and have it build.
