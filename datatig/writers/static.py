from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import shutil
import json

def static_writer(config, datastore):
    # Templates
    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.realpath(__file__)),'statictemplates')),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template_variables = {
        'site_title': config.config.get('title', 'SITE'),
        'site_description': config.config.get('description', ''),
        'site_github_url': config.github_url(),
        'site_github_primary_branch': config.github_primary_branch(),
        'types': {},
        'datastore': datastore,
    }

    for k, v in config.types.items():
        template_variables['types'][k] = {
            'id': k,
            'fields': v.fields,
            'list_fields': v.list_fields(),
        }

    # Out Dir
    os.makedirs(config.out_dir, exist_ok=True)

    # Top Level Static Pages
    for page in ['robots.txt','index.html']:
        with open(os.path.join(config.out_dir, page),"w") as fp:
            fp.write(env.get_template(page).render(**template_variables))

    # Assets
    assets_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'staticassets')
    for filename in [f for f in os.listdir(assets_dir) if os.path.isfile(os.path.join(assets_dir, f))]:
        name_bits = filename.split(".")
        if name_bits[-1] in ['css']:
            shutil.copy(
                os.path.join(assets_dir, filename),
                os.path.join(config.out_dir, filename)
            )

    # Each Type!
    for type in config.types.keys():
        os.makedirs(os.path.join(config.out_dir, 'type', type), exist_ok=True)
        with open(os.path.join(config.out_dir, 'type', type, 'index.html'), "w") as fp:
            fp.write(env.get_template('type/index.html').render(
                type=template_variables['types'][type],
                **template_variables)
            )
        # Each Item!
        for item_id in datastore.get_ids_in_type(type):
            os.makedirs(os.path.join(config.out_dir, 'type', type,'item', item_id), exist_ok=True)
            with open(os.path.join(config.out_dir, 'type', type,'item', item_id, 'index.html'), "w") as fp:
                fp.write(env.get_template('type/item/index.html').render(
                    type=template_variables['types'][type],
                    item_id=item_id,
                    item_data=datastore.get_item(type, item_id),
                    **template_variables)
                )
            with open(os.path.join(config.out_dir, 'type', type, 'item', item_id, 'data.json'), "w") as fp:
                json.dump(datastore.get_item(type, item_id).data, fp, indent=2)