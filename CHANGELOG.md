# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

* A date field in a markdown file does not cause a crash

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
