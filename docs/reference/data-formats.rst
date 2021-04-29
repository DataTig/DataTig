Data Formats
============

This tool works with data stored in several different formats in a git repository. In general these are listed starting with the one we recommend the most, so if you aren't sure start at the top.


YAML files, one per record
--------------------------

Each type of data should have a directory of it's own.

Each record is one file.

The id of each record is part of the name of the file. eg:

#. There is a file `cats/bob.yaml`.
#. The type is configured to be the stored in the directory `cats`.
#. The id of the data is `bob`.

We recommend this because:

* One file per record means that many people editing different records at once will not cause merge request conflicts
* Technically aware humans usually find YAML is easier to read or edit by hand

JSON files, one per record
--------------------------

Each type of data should have a directory of it's own.

Each record is one file.

The id of each record is part of the name of the file. eg:

#. There is a file `cats/bob.json`.
#. The type is configured to be the stored in the directory `cats`.
#. The id of the data is `bob`.

We recommend this because:

* One file per record means that many people editing different records at once will not cause merge request conflicts


