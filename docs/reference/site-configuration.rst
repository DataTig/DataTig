Site Configuration
==================

Location
--------

Each site should have a `datatig.json` or `datatig.yaml` file at it's root. This contains configuration for that site.

The schema of each file is the same.

We recommend using `datatig.yaml` - it is easier to edit, and you can have comments.

General
-------

* `title` - A string. The title of the whole site.
* `description` - A string. A description for the whole site.

A YAML example:

.. code-block:: yaml

    title: Test register
    description: The data for a test

Types
-----

We need to know information about the types of data - think of types like a table in a database.

The `types` key is an array of type information.

Every type has the following options available:

* `id` - every type needs a unique ID.
* `directory` - the directory to look in for data files for this type. Relative to the root of the git repository.
* `fields` - a list of field information. See section below for more.
* `guide_form_xlsx` - A XLSX file to use for generating and importing spreadsheets of a record. See `SpreadSheet forms <https://spreadsheet-forms.readthedocs.io/en/latest/index.html>_`.
* `list_fields` - a list of field id's to show in the static site web interface.
* `json_schema` - a path to a JSON Schema file for this type. Relative to the root of the git repository.
* `pretty_json_indent` - When writing back JSON files, how many spaces to ident by. Defaults to 4.
* `default_format` - When creating new records, what is the default format? 'json', 'md' or 'yaml'. Defaults to 'yaml'.
* `markdown_body_is_field` - When reading or writing markdown files, the body of the MarkDown file is put into a key with this name. Defaults to 'body'.

A YAML example:

.. code-block:: yaml

    types:
    - id: lists
      directory: lists
      list_fields:
      - code
      - title_en
      json_schema: schema/list-schema.json
      pretty_json_indent: 2
      default_format: json

Fields
~~~~~~

Every field needs to be defined.

* `id` - every field needs a unique ID within that type.
* `key` - the path in the data to find this value. Note paths are allowed, not just keys.
* `title` - a title for this field.
* `type` - a type for this field. Defaults to `string`.


Allowed types are:

* `string`
* `url`
* `list-strings`
* `date`
* `datetime`

A YAML example:

.. code-block:: yaml

    types:
    - id: lists
      fields:
      - id: code
        key: code
        title: Code
      - id: title_en
        key: name/en
        title: Name (EN)
      - id: url
        key: url
        title: URL
        type: url
      - id: description_en
        key: description/en
        title: Description (EN)


Git Host
--------

You can specify information about where this git repository is hosted.

Currently the only hosts supported are:
* `GitHub.com <GitHub.com>`_

In a `githost` object, specify the following keys:

* `url` - the URL of the repository. This should not contain the hostname but just the organisation and repository. eg `org-id/register`.
* `primary_branch` - the name of the default or primary branch. Defaults to `main`.

A YAML example:

.. code-block:: yaml

    githost:
        url: org-id/register
        primary_branch: main
