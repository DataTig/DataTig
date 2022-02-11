
const editor_options = {
    startval: data,
    schema: schema,
    theme:'bootstrap4',
    iconlib: "fontawesome5"
};

var editor;

function update() {
    if (data_format == 'json') {
        $('#raw_data_out').val(JSON.stringify(editor.getValue(),null,pretty_json_indent));
    } else if (data_format == 'md') {
        data = editor.getValue();
        if (markdown_body_is_field && markdown_body_is_field in data) {
            body = data[markdown_body_is_field].slice(); // slice is used to get a copy
            delete data[markdown_body_is_field]
            $('#raw_data_out').val("---\n" + jsyaml.dump(data,{'sortKeys':true,'forceQuotes':true})+"---\n\n"+body);
        } else {
            $('#raw_data_out').val("---\n" + jsyaml.dump(data,{'sortKeys':true,'forceQuotes':true})+"---\n");
        }
    } else if (data_format == 'yaml') {
        $('#raw_data_out').val(jsyaml.dump(editor.getValue(),{'sortKeys':true,'forceQuotes':true}));
    }
};

$( document ).ready(function() {
    var element = document.getElementById('editor_holder');
    editor = new JSONEditor(element, editor_options);
    editor.on('change',update);
    update();

    // https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onbeforeunload
    window.addEventListener('beforeunload', function (e) {
      // Cancel the event
      e.preventDefault(); // If you prevent default behavior in Mozilla Firefox prompt will always be shown
      // Chrome requires returnValue to be set
      e.returnValue = '';
    });
});

function copy() {
    update();
    document.getElementById('raw_data_out').select();
    copied = document.execCommand('copy');
    // TODO show user feedback if copied worked/failed
};
