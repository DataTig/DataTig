Encouraging Contributions
=========================

Previous
--------

Before doing this, :doc:`make sure you have done the previous step <deploying-static-site>`.

What this section covers
------------------------

* DataTig can help encourage contributions from people by providing tools and instructions

Tell DataTig where our data lives
---------------------------------

We want to encourage people to contribute new data to this site.

DataTig can help us do this, but before it does that, it needs to know where your data lives.

Edit the `datatig.yml` file. We need to add a new section at the bottom:

.. code-block:: yaml

    githost:
      type: github
      url: xxxxx/yyyyy

Make sure the URL value matches the GitHub repository you created.

Commit this change and push to GitHub.

Now wait a minute until the new version of your static site is rebuilt and deployed.

Go and click on a page for a bike shop. There is a new section, `Edit`.

There is a new button, `Edit Raw data directly on GitHub`. This will take you direct to the relevant file on GitHub.

But also, if you click `Edit in Browser` at the bottom of this page you will see a button to take you to GitHub and instructions for people on how to edit.

This encourages people to edit the data and send you pull requests for you to accept or refuse.

Next
----


:doc:`To continue, visit the next section <using-data>`

