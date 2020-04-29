from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import shutil
import json
from .static_util import jinja2_escapejs_filter
from spreadsheetforms.api import put_data_in_form


class StaticWriter:

    def __init__(self, config, datastore):
        self.config = config
        self.datastore = datastore
        self._template_variables = {}
        self._jinja2_env = None

    def go(self):
        # Templates
        self._jinja2_env = Environment(
            loader=FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.realpath(__file__)),'statictemplates')),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._jinja2_env.filters['escapejs'] = jinja2_escapejs_filter

        self._template_variables = {
            'site_title': self.config.config.get('title', 'SITE'),
            'site_description': self.config.config.get('description', ''),
            'site_github_url': self.config.github_url(),
            'site_github_primary_branch': self.config.github_primary_branch(),
            'types': {},
            'datastore': self.datastore,
        }

        for k, v in self.config.types.items():
            self._template_variables['types'][k] = {
                'id': k,
                'fields': v.fields,
                'list_fields': v.list_fields(),
                'directory': v.directory(),
                'directory_in_git_repository': v.directory_in_git_repository(),
                'guide_form_xlsx': v.guide_form_xlsx(),
                'json_schema': v.json_schema(),
                'pretty_json_indent': v.pretty_json_indent(),
            }
            if v.json_schema():
                with open(os.path.join(self.config.source_dir, v.json_schema())) as fp:
                    self._template_variables['types'][k]['json_schema_string'] = fp.read()

        # Out Dir
        os.makedirs(self.config.out_dir, exist_ok=True)

        # Top Level Static Pages
        for page in ['robots.txt','index.html']:
            self._write_template('', page, page, {})

        # Assets
        assets_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'staticassets')
        for filename in [f for f in os.listdir(assets_dir) if os.path.isfile(os.path.join(assets_dir, f))]:
            name_bits = filename.split(".")
            if name_bits[-1] in ['css','js']:
                shutil.copy(
                    os.path.join(assets_dir, filename),
                    os.path.join(self.config.out_dir, filename)
                )

        # Each Type!
        for type, type_config in self.config.types.items():
            if type_config.guide_form_xlsx():
                guide_form_xlsx = os.path.join(self.config.source_dir, type_config.guide_form_xlsx())

            self._write_template(os.path.join( 'type', type), 'index.html', 'type/index.html', {
                'type': self._template_variables['types'][type]
            })
            self._write_template(os.path.join( 'type', type, 'newweb'), 'index.html', 'type/newweb.html', {
                'type': self._template_variables['types'][type]
            })

            # Each Item!
            for item_id in self.datastore.get_ids_in_type(type):
                # vars
                item_template_vars = {
                    'type': self._template_variables['types'][type],
                    'item_id': item_id,
                    'item_data': self.datastore.get_item(type, item_id),
                    'item_data_json_string': json.dumps(self.datastore.get_item(type, item_id).data),
                }
                # pages
                self._write_template(os.path.join('type', type,'item', item_id), 'index.html', 'type/item/index.html', item_template_vars)
                self._write_template(os.path.join('type', type,'item', item_id, 'editweb'), 'index.html', 'type/item/editweb.html', item_template_vars)
                if type_config.guide_form_xlsx():
                    self._write_template(os.path.join('type', type, 'item', item_id, 'editspreadsheet'), 'index.html',
                                         'type/item/editspreadsheet.html', item_template_vars)
                # data files
                with open(os.path.join(self.config.out_dir, 'type', type, 'item', item_id, 'data.json'), "w") as fp:
                    json.dump(self.datastore.get_item(type, item_id).data, fp, indent=2)
                if type_config.guide_form_xlsx():
                    out_form_xlsx = os.path.join(self.config.out_dir, 'type', type, 'item', item_id, 'data-form.xlsx')
                    put_data_in_form(guide_form_xlsx, self.datastore.get_item(type, item_id).data, out_form_xlsx)

    def _write_template(self, dirname, filename, templatename, variables):
        os.makedirs(os.path.join(self.config.out_dir, dirname), exist_ok=True)
        variables.update(self._template_variables)
        with open(os.path.join(self.config.out_dir, dirname, filename),
                  "w") as fp:
            fp.write(self._jinja2_env.get_template(templatename).render(**variables))

