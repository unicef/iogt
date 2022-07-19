import re


def has_md5_hash(name):
    return bool(re.search(r"\.[a-f0-9]{12}\..*$", name))
