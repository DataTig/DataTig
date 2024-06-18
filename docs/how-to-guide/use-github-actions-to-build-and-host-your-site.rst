Use GitHub actions to build and host your site
==============================================


Scenario
--------

You currently have a DataTig site in a GitHub repository.

You want to build and host the static site online on GitHub Pages.

(In the advanced section, you can learn how to do this at the same time as using another site builder like Jekyll)

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

Advanced - using DataTig at the same time as another site builder such as Jekyll
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To do this, you change the GitHub setting and add a workflow file as before.

However, the workflow file should now build the site twice with 2 different tools.

Here's an example of how to do this, so a Jekyll site is available at the main URL and the DataTig site is available underneath /datatig.

Replace the "Build DataTig site" step of the above file with (edit as directed by the comments):


.. code-block:: yaml

        - name: Make output directory
          run: "mkdir -p _site/datatig"
        - name: Build DataTig site
          # TODO: Replace the URL with the URL of your final site, but leave /datatig at the end
          run: "python -m datatig.cli build . --staticsiteoutput _site/datatig --staticsiteurl https://xxxx.github.io/xxxxxxx/datatig"
        - name: Build Jekyll site
          run: "docker run --rm --volume=\"${{ github.workspace }}:/srv/jekyll:Z\" jekyll/builder:4 /bin/bash -c 'chmod 777 /srv/jekyll && jekyll build _site'"

If you are using Jekyll, the build stage will clear out the DataTig site from the output directory. To stop it doing this, add to your Jekyll `_config.yml`:

.. code-block:: yaml

        keep_files:
         - datatig

(:doc:`For more on using DataTig and Jekyll together, see here <use-with-jekyll-collections>`)

In Tutorial
~~~~~~~~~~~

(Note: :doc:`the contents of this section are also available as part of the tutorial <../tutorial/deploying-static-site>` )
