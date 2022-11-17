import json
import uuid

# we use this simple wrapper for json to handle UUID serialization,
# as well as nested objects without requiring all of our json calls to include this


def serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    return obj.__dict__


def loads(s):
    return json.loads(s)


def dumps(s):
    return json.dumps(s, default=serializer, ensure_ascii=False)
