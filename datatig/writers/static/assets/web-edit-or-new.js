var editor;
var body_editor;
var first_output_data = null;
var current_output_data;

function update() {
    if (data_format == 'json') {
        current_output_data = JSON.stringify(editor.getValue(),null,pretty_json_indent);
    } else if (data_format == 'md') {
        data = editor.getValue();
        if (markdown_body_is_field) {
            current_output_data = "---\n" + jsyaml.dump(data,{'sortKeys':true,'forceQuotes':true})+"---\n\n"+body_editor.value();
        } else {
            current_output_data = "---\n" + jsyaml.dump(data,{'sortKeys':true,'forceQuotes':true})+"---\n";
        }
    } else if (data_format == 'yaml') {
        current_output_data = jsyaml.dump(editor.getValue(),{'sortKeys':true,'forceQuotes':true});
    }
    if (first_output_data === null) {
        first_output_data = current_output_data;
    }
    document.getElementById('raw_data_out').value = current_output_data;
};

function copy() {
    update();
    document.getElementById('raw_data_out').select();
    copied = document.execCommand('copy');
    // TODO show user feedback if copied worked/failed
};

function window_before_unload(e) {
    if (first_output_data != current_output_data) {
        e.preventDefault();
        e.returnValue = '';
    }
}

function start() {
    if (data_format == "md" && markdown_body_is_field) {
        // Start Md Editor
        body_editor = new EasyMDE({
            'element': document.getElementById('editor_body_textarea'),
            'autosave': {
                'enabled': 'default'
            },
            'autoDownloadFontAwesome': false,
            'sideBySideFullscreen': false,
        });
        // Initial value
        if (markdown_body_is_field in data && data[markdown_body_is_field]) {
            body_editor.value(data[markdown_body_is_field]);
        } else {
            body_editor.value("");
        }
        // On update
        body_editor.codemirror.on('change',update);
        // Delete from data we are about to pass to JSON editor
        delete data[markdown_body_is_field];
        // Delete from schema we are about to pass to JSON editor, so user can't select to put it in at the top editor, too!
        if ("properties" in schema && markdown_body_is_field in schema["properties"]) {
            delete schema["properties"][markdown_body_is_field];
        }
    }

    // JSON Editor
    const editor_options = {
        startval: data,
        schema: schema,
        theme:'bootstrap4',
        iconlib: "fontawesome5",
    };
    editor = new JSONEditor(document.getElementById('editor_holder'), editor_options);
    editor.on('change',update);

    // Maybe prompt before user leaves page
    window.addEventListener('beforeunload', window_before_unload);
}

start();
