# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* YAML data files
  * Can read files that are set up to have more than one document, as long as there is only one document in them.
* New local server feature - currently used for internal testing
* Calendars
* Added `timezone` option to `date` and `datetime` fields
* Added `multiline` option to `string` field
* Added `description` option to all fields
* Added `record_id_mode` option to type https://github.com/DataTig/DataTig/issues/13
* Added extra fields to SQLite database to store more of the configuration used when building the site
  * `description`, `sort` and `extra_config` fields to `type_field` table
  * Many fields to `type` table
  * New table `site_config`
* New field type `list-dictionaries`, which lets you also define the fields in the dictionaries.
* New field type `markdown`.
* Exception `SiteConfigurationException` used when something is broken in the site configuration
* Datatig config file is now more forgiving - `type` field on a field on a record accepts any case or extra white space
* A type has a string field automatically added for `markdown_body_is_field` if it is set and the field doesn't already exist. 
  This makes it easier to configure by providing sensible defaults. 
* Edit/New forms now have Markdown editor for markdown body
* Table for `list-string` fields has `sort` column

### Changed

* process.go function, sys_exit -> sys_exit_on_error. Allows other Python code to use this as a library and continue
  if fine but stop and return an error code if not. 
* frictionless data package - all files now start `record_`. This matches the SQLite database and allows us
  to put other files in without possible name collisions.
* Refactored internal Python API
  * Constructor to FieldValueModel has changed
  * `FieldConfigModel.get_value_object_from_record` replaced with `get_value_object` with different parameters, to support `list-dictionaries`
* When turning date fields to timestamps, previously 12:00:00 was assumed to try to avoid timezone issues. 
  Now we have proper timezones, assume 00:00:00
* In `type`, default behavior of `markdown_body_is_field` has changed. 
  Now it defaults to `body` only if `default_format` is Markdown, otherwise it's not set. 
  User can specify `---` to avoid any default value.
* In `type`, default behavior of `list_fields` has changed.
  It now returns the first field rather than an empty list.
* Name of table in output database for `list-string` fields has changed to `record_<type_id>___field_<field_id>`

### Removed

* Dropped support for Python 3.7 as that isn't supported any more.
* Incomplete Guide Form feature.
* Sqlite database drops field `fields` from `type` - it never had any data put in it and thus wasn't used.

### Fixed

* HTML Page titles in static site https://github.com/DataTig/DataTig/issues/18
* With a string list field type, the frictionless data package would have the same specification twice for the extra file.
* Improved performance when parsing date values
* Bug where anything after a "---" in a markdown file body was ignored
* Edit/New forms 
  * Now only prompt you not to leave if you have actually made changes
  * Bug where sometimes markdown content went missing

## [0.5.0] - 2023-01-03

### Added

* Frictionless Data Export
  * Can get via new CLI option to build
  * Included in static site
* SQLite database has foreign keys
* New CLI command "versionedbuild" - currently used for internal testing
* New field type, "integer"
* Datetime and date type fields:
  * Can handle more input formats
  * Provide timestamp info on output (For date fields, time is always set to 12:00)

### Changed

* Refactored internal Python API
  * Moved static writer into new package
  * datatig/readers/directory - def process_type has changed parameters
  * RepositoryAccess split into multiple classes
  * SiteConfigModel, load_from_file now needs a RepositoryAccess instance passed

### Fixed

* Non string (eg integer, list) values in string fields are now read correctly

## [0.4.0] - 2022-05-05

### Changed

* Refactored internal Python API
* Change record_json_schema_validation_error_* table to record_error_*
* Change how record errors shown in static website so it looks more general

### Removed

* Remove undocumented unused feature, git_submodule_directory
* Dropped support for Python 3.6 as that isn't supported any more.
 
### Added

* New field type, "date"
* New field type, "datetime"
* New field type, "boolean"
* Static site: 
  * Show size of SQLite database
  * Errors page shows all errors, site and record

## [0.3.1] - 2022-03-31

### Fixed

* Lock Jinja2 to less than 3.1 as that removes code we use (`jinja2.Markup`)
* A date field in a markdown file does not cause a crash
* On web form for new item, don't have to open "properties" and select keys now

## [0.3.0] - 2022-02-26

### Added

* Data files can be in Markdown (as well as JSON or YAML)
* New '--staticsiteurl' option when building
* YAML files can have .yml extensions as well as .yaml
* JSON API to static site
* Added field columns to record tables in SQLite database
* New field type: "list-strings"
* If JSON Schema not supplied, build one automatically from fields. This means the edit features and validation are now always available.

### Fixed

* Fields of different types are shown correctly when listing records on a type page

## [0.2.0] - 2021-07-22

### Changed

* Removed `datatig-cli.py` - call via `python -m datatig.cli` instead 

### Fixed

* Fixed crash when tool run and a JSON Schema was not specified
* Use correct JSON Schema validator (previously it always used Draft 3)

## [0.1.1] - 2021-04-15

### Fixed

* Fixed Python packaging error that meant 0.1.0 was not packaged correctly

## [0.1.0] - 2021-04-15

### Changed

* **BREAKING CHANGE:** The cli script call for build has changed to have a --staticsiteoutput option.
* Updated to latest version of json-editor https://github.com/DataTig/DataTig/issues/5
* Types have a "default_format" option, "json" or "yaml". Previously default was "json", now it is "yaml".
* New config setting "primary_branch". Previously default was "master", now it is "main".

### Added

* SQLite output mode via the --sqliteoutput option
* Supports reading and writing YAML files
* Exception for duplicate ID's
* Check mode
* Errors found when loading will now not stop process; process will finish, with errors logged


## [0.0.4] - 2021-04-14

First release with changelog
