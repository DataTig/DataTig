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

    python -m datatig.cli build . --staticsiteoutput _site
    sh -c "cd _site && python3 -m http.server"

This is great, but it's not great we have to remember to update this. Also, this is only available to you. Let's make this website available to everyone.

Fortunately, there are several services that will help with this. We will use one called Netlify.

Go to https://www.netlify.com/ and sign up using your GitHub login.

You will be given the option of creating a new website.

Do so, and pick the repository we have created.

It will now try and build the website and fail, because we haven't told it how to.

In the top level of the repository, create a file `netlify.toml`. It's contents should be:

.. code-block:: toml

    [build]
      publish = "out"
      command = "pip install datatig && export PYTHONPATH=$(pwd) && python -m datatig.cli build . --staticsiteoutput out"

In the top level of the repository, create a file `runtime.txt`. It's contents should be:


.. code-block:: text

    3.9

This should be a single line, with no extra spaces. It tells Netlify which version of Python to use.

Commit your files `netlify.toml` and `runtime.txt` and push them to GitHub.

In Netlify, you should be able to go to your site and see that a new build is running. This time, it should succeed.

You should be able to click on the address and see this website online.

As you have just seen, any change in GitHub will trigger a build on your website in Netlify, so that this website is kept up to date.

Next
----


:doc:`To continue, visit the next section <encouraging-contributions>`

