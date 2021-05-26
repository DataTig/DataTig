Use GitHub actions to check your data
=====================================


Scenario
--------

You currently have a DataTig site in a GitHub repository.

You want to make sure the data is correct, at all times and when someone makes a pull request.

You can set up GitHub Actions to check this for you.

Steps
-----

Create a YAML file in the GitHub repository.

It must be in the directory: `.github/workflows/`

It must have a YAML extension but it can have any file name you want. We suggest: `check.yml`

The contents should be:

.. code-block:: yaml

    name: Check
    on: [push, pull_request]

    jobs:
      check:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v2
        - name: Setup python
          uses: actions/setup-python@v2
          with:
            python-version: 3.9
            architecture: x64

        - run: pip install datatig
        - run: python -m datatig.cli check .

Commit this and merge it into your default branch (`main`, or whatever you use).

That's it!

Note that pull requests will only be checked if this file is in the code the pull request is based on. In other words, existing pull requests may not be checked. If you have an existing pull request that you would like to be checked, you must rebase it onto a version of the data that does have the above file in it.


Optionally: Require checks to pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can set GitHub to require this check to pass before code is merged.

Before doing this, the check must have run at least once.

To do so:

#. Go to the GitHub repository; eg https://github.com/xxx/yyyy
#. Click `Settings`
#. Click `Branches`
#. In the `Branch protection rules` section either add a new rule for the branch you want, or edit the existing rule
#. Select `Require status checks to pass before merging`
#. Select `check`
#. Save changes

In Tutorial
~~~~~~~~~~~

(Note: :doc:`the contents of this section are also available as part of the tutorial <../tutorial/checking-data-automatically>` )
