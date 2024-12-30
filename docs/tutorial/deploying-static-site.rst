Deploying the Static Site
=========================

Previous
--------

Before doing this, :doc:`make sure you have done the previous step <checking-data-automatically>`.


What this section covers
------------------------

* We have seen how to build a website for this manually; lets put this website online automatically


Setting up the website
----------------------

We have seen how to manually build the website and see it on your computer.

.. code-block:: bash

    python -m datatig build . --staticsiteoutput _site
    sh -c "cd _site && python3 -m http.server"

This is great, but it's not great we have to remember to update this. Also, this is only available to you. Let's make this website available to everyone.

Fortunately, GitHub Pages and Actions can be used to do this. You need to change a setting in GitHub and create a GitHub Actions file.

In the repository on GitHub, go to settings, pages and for the “source” option select “Github Actions”.

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
          run: "python -m datatig build . --staticsiteoutput _site --staticsiteurl https://xxxx.github.io/yyyyyyy"
        - name: Upload Artifact
          uses: actions/upload-pages-artifact@v3
          with:
            path: "./_site"
        - name: Deploy to GitHub Pages
          id: deployment
          uses: actions/deploy-pages@v4

Commit your new file and push it to GitHub.

In the repository on GitHub, you should be able to go to the Actions tab. It may take a few minutes the first time, but you should a new build appear and succeed.

You should be able to visit https://xxxx.github.io/yyyyyyy  and see this website online.

As you have just seen, any change in GitHub will trigger a build on your website so that this website is kept up to date.

(Note: :doc:`the contents of this section are also available as part of the how-to section <../how-to-guide/use-github-actions-to-build-and-host-your-site>` )

Next
----


:doc:`To continue, visit the next section <encouraging-contributions>`

