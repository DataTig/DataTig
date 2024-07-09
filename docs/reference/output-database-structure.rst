Output Database Structure
=========================

When run, a database is created with all the details of the site and the data. This page describes the structure of that
database.

Sometimes the id of a DataTig type or field is used in a database table or column name.
In these cases, it is followed by 3 underscores (`___`).
This clearly separates the 2 parts and avoids potential name clashes.

Table `type`
~~~~~~~~~~~~

This lists all the different types defined.

It has the following columns:

* `id`
* `directory`
* `json_schema`
* `list_fields`
* `pretty_json_indent`
* `default_format`
* `markdown_body_is_field`

Table `type_field`
~~~~~~~~~~~~~~~~~~

This lists all the fields defined for each type.

It has the following columns:

* `type_id`
* `id`
* `key`
* `type`
* `title`
* `description`
* `sort`
* `extra_config`

Tables `record_<type_id>`
~~~~~~~~~~~~~~~~~~~~~~~~

For each type, a different table is created. This is because each type table will have different columns depending on
which fields it has, and to allow for easier querying.


It has the following columns:

* `id`
* `data`
* `git_filename`
* `format`

Each field will have one of more columns for it. Generally fields have one column of the best type, called `field_<field_id>`.

Fields of type `datetime` or `date` will have several columns:

* `field_<field_id>` String, in ISO format.
* `field_<field_id>___timestamp` Integer, the timestamp of this value.

Tables `record_<type_id>___field_<field_id>`, for record fields with multiple values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fields that can have multiple values have extra tables. This is to allow for easier querying, and in some cases because
tables will have different columns depending on which fields are defined.

For fields of type `list-strings`, the table is called `record_<type_id>___field_<field_id>`. It has the following columns:

* `record_id`
* `value`

For fields of type `list-dictionaries`, the table is called `record_<type_id>___field_<field_id>`.  It has the following columns:

* `record_id`
* `sort` Integer.
* extra columns for the fields in the dictionary.

Tables `record_error_<type>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each type, a different table is created. This is to allow for easier querying.

It has the following columns:

* `record_id`
* `message`
* `data_path`
* `schema_path`
* `generator`

Table `error`
~~~~~~~~~~~~~

This lists any errors encountered when processing the site that can't be linked directly to a record.

It has the following columns:

* `filename`
* `message`

Table `site_config`
~~~~~~~~~~~~~~~~~~~

This lists any values for the site configuration that aren't expressed in other tables (for example, `type` or `type_field`).

It has the following columns:

* `key`
* `value`

Table `calendar`
~~~~~~~~~~~~~~~~

This table always exists, so you can easily query it

It has the following columns:

* `id`
* `timezone`

Table `calendar_event`
~~~~~~~~~~~~~~~~~~~~~~

This table only exists if any calendars are actually defined.
This avoids cluttering up the database with too many tables that would never be used and confusing people.

It has the following columns:

* `calendar_id`
* `id`
* `summary`
* `start_iso`
* `start_timestamp`
* `end_iso`
* `end_timestamp`
* `record_<type_id>___id`
