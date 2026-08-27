"""Small language helpers shared across UI feature catalogues."""

def _lang_text(lang,fr,en,de,es):
    return {'fr':fr,'en':en,'de':de,'es':es}.get(lang,en)
