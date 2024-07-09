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
* `list_fields` - a list of field id's to show in the static site web interface.
* `json_schema` - a path to a JSON Schema file for this type. Relative to the root of the git repository.
* `pretty_json_indent` - When writing back JSON files, how many spaces to ident by. Defaults to 4.
* `default_format` - When creating new records, what is the default format? 'json', 'md' or 'yaml'. Defaults to 'yaml'.
* `markdown_body_is_field` - When reading or writing markdown files, the body of the markdown file is put into a key with this name. Defaults to `body`. Set to `---` (3 dashes) to turn this off and make sure no default is used.
* `record_id_mode` - When creating an id for a file, whether to include any directories it may be in too. Can be `directory_and_filename` or `filename_only`. Defaults to `directory_and_filename`.

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
------

Every field needs to be defined. Every field type has these options:

* `id` - every field needs a unique ID within that type.
* `key` - the path in the data to find this value. Note paths are allowed, not just keys.
* `title` - a title for this field.
* `description` - a description for this field.
* `type` - a type for this field. Defaults to `string`.

Some field types have extra options. See below for details.

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
        multiline: True

Field Type `string`
~~~~~~~~~~~~~~~~~~~

The type `string` has the following extra options:

* `multiline`: Defaults to false. Whether new lines are allowed in values

Field Type `url`
~~~~~~~~~~~~~~~~

There are no extra configuration options.

Field Type `date`
~~~~~~~~~~~~~~~~~

The types `date` and `datetime` have the following extra options:

* `timezone`: Defaults to `UTC`. Set to a location string like `Europe/Berlin`

Field Type `datetime`
~~~~~~~~~~~~~~~~~~~~~

The types `date` and `datetime` have the following extra options:

* `timezone`: Defaults to `UTC`. Set to a location string like `Europe/Berlin`

Field Type `boolean`
~~~~~~~~~~~~~~~~~~~~

There are no extra configuration options.

Field Type `integer`
~~~~~~~~~~~~~~~~~~~~

There are no extra configuration options.

Field Type `markdown`
~~~~~~~~~~~~~~~~~~~~~

There are no extra configuration options.

Field Type `list-strings`
~~~~~~~~~~~~~~~~~~~~~~~~~

There are no extra configuration options.

Field Type `list-dictionaries`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As well as `list-dictionaries`, a type of `list-dicts` can be used for short.

The type `list-dictionaries` has the following extra options:

* `fields`: A list of fields to be found in the dictionary items. Definition is the same as above, but list types are not allowed. (So you can't have a list in a list.)

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

.. _reference_site_configuration_calendars:

Calendars
---------

More about :ref:`explanation_calendars`.

You can define multiple calendars. Each calendar should have an id.
Each calendar can have multiple sources of data, and each source of data should define which type to look in and which fields in the data to map to fields in the calendar.

In a `calendars` object, specify the `id` of the calendar then an object to configure it. Each object should have:

* `datas`: a list of data sounces; see below.
* `timezone`: Defaults to `UTC`. Set to a location string like `Europe/Berlin`. Ideally also set the same timezone on the start and end fields you will be using.

Each item in the  `datas` list can have the following keys.

* `type` (required) - The id of the type to get data from.
* `start` (optional, defaults to `start`) - the field name to use to look up the start date of the event.
* `end` (optional, defaults to `end`) - the field name to use to look up the end date of the event.
* `summary` (optional, defaults to `summary`) - the field name to use to look up the summary title of the event.
* `id` (optional, defaults to `{{type_id}}_{{record_id}}@example.com`) - the template to use to create an id for each event.

Field names given should not be of one of the list types.

`ids` of each event should be defined to be unique in each calendar, and the following place holders can be used:

* `{{record_id}}` - the id of the record
* `{{type_id}}` - the id of the type

A YAML example:

.. code-block:: yaml

    calendars:
      main:
        timezone: Europe/Berlin
        datas:
          - type: events
            summary: title
      deadlines:
        timezone: Europe/Berlin
        datas:
          - type: events
            summary: title
            start: submission_deadline
            end: submission_deadline
            id: "deadline_ID@example.com"

This defines 2 calendars, one with the id `main` and one with the id `deadlines`.

Given an data item like:

.. code-block:: yaml

    title: Python Conference
    start: 2024-07-01T10:00:00
    end: 2024-07-01T11:00:00
    submission_deadline: 2024-01-05

You can see that the same data item creates an event on the `main` calendar with the start and end dates,
but also creates a different event on the  `deadlines` calendar at the date of the deadline for the conference.
