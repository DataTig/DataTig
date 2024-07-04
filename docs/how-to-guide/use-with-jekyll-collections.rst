Use with Jekyll Collections
===========================

Scenario
--------

The Jekyll site builder has a feature of collections, where related content can be stored in separate files in a git repository and used in a Jekyll site. https://jekyllrb.com/docs/collections/

If you are crowd sourcing data this way, you can also use DataTig along side Jekyll.

This will let you carry on producing the custom Jekyll website you already have, whilst using DataTig
to help people:

* contribute new data or edit existing data
* check data quality
* transform the data into more useful forms for everyone to re-use.

Steps
-----

Take the existing Jekyll site, and add a `datatig.yaml` config file at the root.

Define a type with the fields used in the collection. (:doc:`Configuration Reference<../reference/site-configuration>`)

You can then set up DataTig in various ways with the existing Jekyll site, such as:

* Setting up DataTig to check the quality of the data (:doc:`How to do this with GitHub Actions<use-github-actions-to-check-your-data>`)
* Building a static DataTig site in a subdirectory underneath the Jekyll site (:doc:`How to do this with GitHub Actions<use-github-actions-to-build-and-host-your-site>`)

Example
-------

A Jekyll site lists events. In the `_event` directory, a file called `2026-04.md` has the following contents:

.. code-block:: yaml

    ---
    layout: event
    start: 2026-04-19 19:00
    end: 2026-04-19 21:00
    title: April Example meetup
    location: Example address
    ---

    Some details of the event.

This collection is referenced in the Jekyll configuration file `_config.yml`:

.. code-block:: yaml

    collections:
      event:
        output: true
        sort_by: start

Here's a snippet of the Jekyll layout file `_layouts/event.html` that is used to output a custom page for each event in the Jekyll site:

.. code-block:: html

    ---
    layout: default
    ---

        <h2>{{ page.title }}</h2>

        <ul>
            <li>
                <span>{{ page.start | date: "%l:%M%p %a %e %b %Y" }}</span>
                -
                <span>{{ page.end | date: "%l:%M%p %a %e %b %Y" }}</span>
            </li>
            {% if page.location %}
                <li>{{ page.location }}</li>
            {% endif %}
        </ul>

        {{ content }}


Given this Jekyll site, you now need to define a `datatig.yaml` file with a type and details of the fields.

The following `datatig.yaml` file will collect all the events into a DataTig site, and also add them to a calendar:


.. code-block:: yaml

    types:
    - id: event
      directory: _event
      default_format: md
      markdown_body_is_field: content
      fields:
        - id: title
          key: title
          title: Title
        - id: content
          key: content
          title: Content
        - id: location
          key: location
          title: Location
        - id: start
          key: start
          title: Start
          type: datetime
          timezone: Europe/London
        - id: end
          key: end
          title: End
          type: datetime
          timezone: Europe/London
    calendars:
      main:
        timezone: Europe/London
        datas:
          - type: event
            summary: title
            start: start
            end: end
            id: "event_{{record_id}}@example.com"
