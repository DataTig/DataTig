import os

from flask import Flask, send_from_directory  # type: ignore
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore

# TODO should this be in a better package?
from datatig.writers.static.static_util import jinja2_escapejs_filter

from .view_index import ViewIndex
from .view_type_index import ViewTypeIndex
from .view_type_record_editweb import ViewTypeRecordEditWeb
from .view_type_record_index import ViewTypeRecordIndex

jinja2_env = Environment(
    loader=FileSystemLoader(
        searchpath=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "templates"
        )
    ),
    autoescape=select_autoescape(["html", "xml"]),
)
jinja2_env.filters["escapejs"] = jinja2_escapejs_filter

app = Flask(__name__)

# -----------------------------------------------------------  Index & misc

app.add_url_rule("/", view_func=ViewIndex.as_view("index", jinja2_env))

# -----------------------------------------------------------  Type

app.add_url_rule(
    "/type/<type_id>/",
    view_func=ViewTypeIndex.as_view("type_index", jinja2_env),
    methods=["GET"],
)

# -----------------------------------------------------------  Record

app.add_url_rule(
    "/type/<type_id>/record/<record_id>/",
    view_func=ViewTypeRecordIndex.as_view("type_record_index", jinja2_env),
    methods=["GET"],
)

app.add_url_rule(
    "/type/<type_id>/record/<record_id>/editweb",
    view_func=ViewTypeRecordEditWeb.as_view("type_record_editweb", jinja2_env),
    methods=["GET", "POST"],
)

# -----------------------------------------------------------  Static


@app.route("/css/<path:path>")
def static_css(path):
    return send_from_directory("static/css", path)


@app.route("/js/<path:path>")
def static_js(path):
    return send_from_directory("static/js", path)
