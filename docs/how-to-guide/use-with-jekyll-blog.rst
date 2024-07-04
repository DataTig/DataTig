Use with Jekyll Blog
====================

Scenario
--------

The Jekyll site builder has a blog feature, where each post is stored in a markdown file. https://jekyllrb.com/docs/posts/
(Jekyll can support other formats, but the only format both currently support is markdown.)

You can use Jekyll to produce a custom website for your blog, whilst using DataTig to help people edit the posts or create new ones.

Steps
-----

Take the existing Jekyll site, and add a `datatig.yaml` config file at the root.

Define a type for the blog posts used in the collection. (:doc:`Configuration Reference<../reference/site-configuration>`)

* `default_format` should be set to `md`. This makes sure any new files created are in markdown format.
* For fields, define the extra fields your blog uses which should be set in a YAML block at the top of the file. Jekyll calls this "front matter". https://jekyllrb.com/docs/front-matter/

You can then set up DataTig in various ways with the existing Jekyll site, such as:

* Building a static DataTig site in a subdirectory underneath the Jekyll site (:doc:`How to do this with GitHub Actions<use-github-actions-to-build-and-host-your-site>`)

If you don't want the `datatig.yaml` file to appear in the output site, you can add it to the `exclude` key in `_config.yml`.

Example
-------

For `datatig.yaml`:

.. code-block:: yaml

    types:
    - id: blog
      directory: _posts
      default_format: md
      # If we don't set markdown body, a default of `body` is used.
      markdown_body_is_field: content
      fields:
        # These are fields we use in our "front matter".
        # This example has a title and description,
        # to use when listing blog posts.
        # Your blog may have other fields - define them here.
        - id: title
          key: title
          title: Title
        - id: description
          key: description
          title: Description
        # This field will hold the markdown body for us.
        # If we don't specify it it will be added automatically.
        # But we can change it if we want.
        - id: content
          key: content
          title: Content
          multiline: True
        # Often with blog posts you always want a `layout`
        # field which is set to a specific value.
        # There is no feature in DataTig to do this automatically
        # for us yet, so for now we'll just add a field
        # and tell people what value it should have.
        - id: layout
          key: layout
          title: layout
          description: This should always be set to blog

To stop the `datatig.yaml` file appearing in the output site, add to `_config.yml`:

.. code-block:: yaml

    exclude:
      - datatig.yaml

Real Example
------------

DataTig's own website is set up in this way. You can view it's source at https://github.com/DataTig/datatig.github.io

You can see the static website output of the Python library at https://www.datatig.com/datatig_for_this_website/


