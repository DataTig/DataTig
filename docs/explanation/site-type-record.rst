Site, Types and Records
=======================

Site
----

Each site is a separate website and data repository.

It should ideally be in one git repository by itself - so one git repository should be thought of as one site.

You can think of sites like a whole database in a database system.

Type
----

Each site can have multiple types of data in it.

Each type has it's own set of configuration, rules and guidance.

When a site is build, the data for each type is held separately for easy querying.

Each type is identified by it’s id, which should be unique.

Each type has a:

* id
* title
* a directory set - this is where in the git repository it's data is stored
* a JSON Schema - if this is included, any data will be validated against it and a web editor will be available
* a default format that should be used when creating new records (eg YAML or JSON)
* a guide spreadsheet - TODO
* a list of field definitions, and which fields to show when listing the data

You can think of types like a table in a database system.

Field
-----

Each type can have a list of field definitions.

These define interesting data to pull out.

Note that there is currently some duplication between the definition of these and the JSON Schema definition.

Record
------

Each Type can have multiple records of data.

Each record is identified by it’s id, which should be unique within it’s type.

Each record has a:

* id
* data, which can be edited as a whole and also from which values for each field are extracted

You can think of types like an individual row in a table in a database system.
