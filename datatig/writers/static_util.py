import jinja2

#### FROM https://stackoverflow.com/questions/12339806/escape-strings-for-javascript-using-jinja2
_js_escapes = {
        '\\': '\\u005C',
        '\'': '\\u0027',
        '"': '\\u0022',
        '>': '\\u003E',
        '<': '\\u003C',
        '&': '\\u0026',
        '=': '\\u003D',
        '-': '\\u002D',
        ';': '\\u003B',
        u'\u2028': '\\u2028',
        u'\u2029': '\\u2029'
}
# Escape every ASCII character with a value less than 32.
_js_escapes.update(('%c' % z, '\\u%04X' % z) for z in range(32))
def jinja2_escapejs_filter(value):
        retval = []
        for letter in value:
                if letter in _js_escapes:
                        retval.append(_js_escapes[letter])
                else:
                        retval.append(letter)

        return jinja2.Markup("".join(retval))