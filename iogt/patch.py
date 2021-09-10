from translation_manager import utils


def get_dirname_from_lang(lang):
    "Converts lang in format en-gb to format en_GB"

    return lang


def get_lang_from_dirname(dirname):
    "Converts lang in format en_GB to format en-gb"
    return dirname


utils.get_dirname_from_lang = get_dirname_from_lang
utils.get_lang_from_dirname = get_lang_from_dirname
