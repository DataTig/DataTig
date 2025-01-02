
const editor_options = {
    startval: data,
    schema: schema,
    theme:'bootstrap4',
    iconlib: "fontawesome5"
};

var editor;

function update() {
    $('#raw_data_out').val(JSON.stringify(editor.getValue(),null,pretty_json_indent));q
};

$( document ).ready(function() {
    var element = document.getElementById('editor_holder');
    editor = new JSONEditor(element, editor_options);
    editor.on('change',update);
    update();
});
