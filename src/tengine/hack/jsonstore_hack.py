import jsonstore
from functools import partial


def fix_jsonstore_dumps():
    # Fix an issue of jsonstore dumping non-ASCII ugly text, like '\u2321'
    jsonstore.json.dumps = partial(jsonstore.json.dumps, ensure_ascii=False)
