Specifying Structure
====================

Previous
--------

Before doing this, :doc:`make sure you have done the previous step <setting-up-site-and-adding-first-data>`.


What this section covers
------------------------

*  Telling DataTig about the structure of your data so it can be more helpful

Adding a JSON Schema
--------------------

JSON is a standard way of representing data, for example:

.. code-block:: json

    {
        "title": "Bob's Bikes",
        "url": "http://www.bobsbikeshop.co.uk/"
    }

(If you want to, you can work with JSON files in your repository. You could delete the `bobs-bikes.yaml` file you have and add a `bobs-bikes.json` file with the above contents and the project would have exactly the same data. However we recommend you work with YAML files, as they are easier for humans to edit.)

JSON Schema is a way you can specify that your JSON Data should have a certain structure. You can provide information on fields, specify a value must be set or specify the format the value must be in.

Every item in a DataTig repository is internally converted to JSON and checked against a JSON Schema you specify. This means that DataTig can help you check and enforce all the data that people try to add to your repository.

First, create a file called `shop.schema.json`. It's contents should be:

.. code-block:: json

    {
      "$schema": "http://json-schema.org/draft-03/schema#",
      "title": "Shop",
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The name of the shop.",
          "minLength": 1
        },
        "url": {
          "type": "string",
          "description": "A URL of a website where you can find out about this shop.",
          "minLength": 1
        }
      },
      "required": [
        "title",
        "url"
      ]
    }

Then we need to tell DataTig to use this file. Edit `datatig.yml`. Add in the line about `json_schema`:

.. code-block:: yaml

    title: Local Cycling Resources in CityCity
    description: Listing all the useful cycling resources in CityCity
    # Every type of data we list should have an entry here
    types:
    # This defines the shops data
    # Every type should have an unique identifier
    - id: shops
      # For every type, we need to know in which directory we can find the data
      directory: shops
      # For a type, optionally tell it about a JSON Schema
      json_schema: shop.schema.json

Finally, we are going to create some incomplete data so you can see what it looks like when a check has failed.

Create a file called `cathy-cathode.yaml` in the `shops` directory. For the contents, put:

.. code-block:: yaml

    title: Cathy Cathode

(There is no URL because we don't know of a website for Cathy's shop!).

Now run the check function again. This time, the tool should tell you there is a problem with a bit of data.

.. code-block:: bash

    python -m datatig.cli check .


TODO put example error output here!

Adding a JSON Schema also does some other things to encourage contributions, which we will see later.

For now, commit your files `cathy-cathode.yaml`,  `datatig.yml` and `shop.schema.json` and push them to GitHub.

Adding Fields Definitions
-------------------------

It can be difficult to write JSON Schema. There is an easier way to specify which fields your data has.

 Edit `datatig.yml`. Add in the section about `fields` and `list_fields`:

.. code-block:: yaml

    title: Local Cycling Resources in CityCity
    description: Listing all the useful cycling resources in CityCity
    # Every type of data we list should have an entry here
    types:
    # This defines the shops data
    # Every type should have an unique identifier
    - id: shops
      # For every type, we need to know in which directory we can find the data
      directory: shops
      # For a type, optionally tell it about a JSON Schema
      json_schema: shop.schema.json
      # Define some fields
      fields:
      # Every field should have an unique identifier
      - id: title
        # For each field, we need to tell it where in the data to look for the value.
        key: title
        # For each field, we should give it a friendly title
        title: Title of Shop
      - id: url
        key: url
        title: URL of Website about Shop
      # We need to tell DataTig which fields are important to list when looking at a list of all the data.
      list_fields:
      - title

In the fields section, we can tell DataTig about as many fields as you want.

Now let's build the website again and look at it. This is the same instructions as the previous step - they are:

.. code-block:: bash

    python -m datatig.cli build . --staticsiteoutput _site
    sh -c "cd _site && python3 -m http.server"

Now, when you open a web browser and go to http://localhost:8000/type/shops you should be able to see more information. The titles of the shops should also be on this page now. (The URL's aren't because that was not included in `list_fields`)

TODO screenshot?

Click on a shop, and you should see some more information again.

Next
----


:doc:`To continue, visit the next section <checking-data-automatically>`

