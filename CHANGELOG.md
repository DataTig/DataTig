# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
