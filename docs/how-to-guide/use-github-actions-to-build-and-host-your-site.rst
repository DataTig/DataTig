Use GitHub actions to build and host your site
==============================================


Scenario
--------

You currently have a DataTig site in a GitHub repository.

You want to build and host the static site online on GitHub Pages.

Steps
-----

You need to change a setting in GitHub and create a GitHub Actions file.

GitHub Setting
~~~~~~~~~~~~~~

In the repository on GitHub, go to settings, pages and for the “source” option select “Github Actions”.

Actions file
~~~~~~~~~~~~

Create a YAML file in the GitHub repository.

It must be in the directory: `.github/workflows/`

It must have a YAML extension but it can have any file name you want. We suggest: `build_and_deploy.yml`

The contents should be (edit as directed by the comments):

.. code-block:: yaml

    name: Build and Deploy
    on:
      push:
         branches:
            # TODO: Change main to the name of your default branch.
            - main

    jobs:
      build_deploy:
        runs-on: ubuntu-latest
        permissions:
          pages: write
          id-token: write
        steps:
        - uses: actions/checkout@v4
        - name: Setup python
          uses: actions/setup-python@v2
          with:
            python-version: 3.12
            architecture: x64
        - name: Install DataTig
          run: "pip install datatig"
        - name: Build DataTig site
          # TODO: Replace the URL with the URL of your final site.
          run: "python -m datatig.cli build . --staticsiteoutput _site --staticsiteurl https://xxxx.github.io/xxxxxxx"
        - name: Upload Artifact
          uses: actions/upload-pages-artifact@v3
          with:
            path: "./_site"
        - name: Deploy to GitHub Pages
          id: deployment
          uses: actions/deploy-pages@v4


Commit this and merge it into your default branch (`main`, or whatever you use).

That's it!


In Tutorial
~~~~~~~~~~~

(Note: :doc:`the contents of this section are also available as part of the tutorial <../tutorial/deploying-static-site>` )
