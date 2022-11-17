import datetime
import iso8601
import uuid

import ucjson

class GenerationPolicy:
    id: uuid.UUID
    name: str
    function: str
    parameters: str

    def __init__(self, id, name='', function='', parameters=''):
        self.id = id
        self.name = name
        self.function = function
        self.parameters = parameters


    def __repr__(self):
        return f"GenerationPolicy({self.id})"


    def to_json(self):
        return ucjson.dumps(
            {
                "id": str(self.id),
                "name": self.name,
                "function": self.function,
                "parameters": self.parameters
            },
            default=seralizer,
            ensure_ascii=False
        )


    @staticmethod
    def from_json(j):
        return GenerationPolicy(
            uuid.UUID(j['id']),
            j['name'],
            j['function'],
            j['parameters']
        )


class AccessPolicy:
    id: uuid.UUID
    name: str
    function: str
    parameters: str
    version: int


    def __init__(self, id, name='', function='', parameters='', version=1):
        self.id = id
        self.name = name
        self.function = function
        self.parameters = parameters
        self.version = version


    def __repr__(self):
        return f"AccessPolicy({self.id})"


    def to_json(self):
        return ucjson.dumps(
            {
                "id": str(self.id),
                "name": self.name,
                "function": self.function,
                "parameters": self.parameters,
                "version": self.version
            },
            default=serializer,
            ensure_ascii=False
        )

    @staticmethod
    def from_json(j):
        return AccessPolicy(
            uuid.UUID(j['id']),
            j['name'],
            j['function'],
            j['parameters'],
            j['version']
        )


# Note: this is a slightly weird place for this, but it's a structured body that can use
# a formal wrapper, and putting it in "requests.py" causes some annoying namespace issues.
class InspectTokenResponse:
    id: uuid.UUID
    token: str

    created: datetime.datetime
    updated: datetime.datetime

    generation_policy: GenerationPolicy
    access_policy: AccessPolicy

    def __init__(self, id, token, created, updated, generation_policy, access_policy):
        self.id = id
        self.token = token

        self.created = created
        self.updated = updated

        self.generation_policy = generation_policy
        self.access_policy = access_policy


    def to_json(self):
        return ucjson.dumps({
            "id": str(self.id),
            "token": self.token,
            "created": self.created,
            "updated": self.updated,
            "generation_policy": self.generation_policy.__dict__,
            "generation_policy": self.access_policy.__dict__
        }, ensure_ascii=False)


    @staticmethod
    def from_json(j):
        return InspectTokenResponse(
            uuid.UUID(j['id']),
            j['token'],
            iso8601.parse_date(j['created']),
            iso8601.parse_date(j['updated']),
            GenerationPolicy.from_json(j['generation_policy']),
            AccessPolicy.from_json(j['access_policy'])
        )
