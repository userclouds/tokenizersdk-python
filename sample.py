import functools
import uuid

from client import Client, Error
from models import AccessPolicy, GenerationPolicy
from policies import AccessPolicyOpen, GenerationPolicyUUID

client_id = "<REPLACE ME>"
client_secret = "<REPLACE ME>"
url = '<REPLACE ME>'

def test_access_policies(c: Client):
    # we embed the ID in a comment to ensure we are creating a unique AP each time
    id = uuid.uuid4()
    new_ap = AccessPolicy(id, "test access policy", f"function policy(x, y) {{ return false /* {id} */}};", "{}")

    try:
        created_ap = c.CreateAccessPolicy(new_ap)
        if created_ap.id != new_ap.id:
            print(f"create changed id from {new_ap.id} to {created_id.id}")
    except Error as e:
        print("failed to create new access policy: ", e)

    aps = []
    try:
        aps = c.ListAccessPolicies()
    except Error as e:
        print("failed to list access policies: ", e)

    if not functools.reduce(lambda found, ap: found or (ap.id == AccessPolicyOpen.id), aps):
        print("missing AccessPolicyOpen in list: ", aps)
    if not functools.reduce(lambda found, ap: found or (ap.id == created_ap.id), aps):
        print("missing new access policy in list: ", aps)

    created_ap.parameters = '{"foo": "bar"}'

    try:
        update = c.UpdateAccessPolicy(created_ap)
        if update.id != created_ap.id:
            print(f"update changed ID from {created_ap.id} to {update.id}")
        if update.version != created_ap.version + 1:
            print(f"update changed version from {created_ap.version} to {update.version}, expected +1")
    except Error as e:
        print("failed to update access policy: ", e)

    try:
        if not c.DeleteAccessPolicy(update.id):
            print("failed to delete access policy but no error?")
    except Error as e:
        print("failed to delete access policy: ", e)


def test_generation_policies(c: Client):
     # we embed the ID in a comment to ensure we are creating a unique AP each time
    id = uuid.uuid4()
    new_gp = GenerationPolicy(id, "test generation policy", f"function policy(x, y) {{ return 'token' /* {id} */}};", "{}")

    try:
        created_gp = c.CreateGenerationPolicy(new_gp)
        if created_gp.id != new_gp.id:
            print(f"create changed id from {new_gp.id} to {created_id.id}")
    except Error as e:
        print("failed to create new generation policy: ", e)

    gps = []
    try:
        gps = c.ListGenerationPolicies()
    except Error as e:
        print("failed to list generation policies: ", e)

    if not functools.reduce(lambda found, gp: found or (gp.id == GenerationPolicyUUID.id), gps):
        print("missing GenerationPolicyUUID in list: ", gps)
    if not functools.reduce(lambda found, gp: found or (gp.id == created_gp.id), gps):
        print("missing new generation policy in list: ", gps)

    try:
        if not c.DeleteGenerationPolicy(new_gp.id):
            print("failed to delete generation policy but no error?")
    except Error as e:
        print("failed to delete generation policy: ", e)


def test_token_apis(c: Client):
    originalData = "something very secret"
    token = c.CreateToken(originalData, GenerationPolicyUUID, AccessPolicyOpen)
    print(f"Token: {token}")

    data = c.ResolveToken(token, {})
    print(f"Data: {data}")

    if(data != originalData):
        print("something went wrong")

    lookup_token = None
    try:
        lookup_tokens = c.LookupToken(originalData, GenerationPolicyUUID, AccessPolicyOpen)
    except Error as e:
        print("failed to lookup token: ", e)

    if token not in lookup_tokens:
        print(f"expected lookup tokens {lookup_token} to contain created token {token}")

    itr = None
    try:
        itr = c.InspectToken(token)
    except Error as e:
        print("failed to inspect token: ", e)

    if itr.token != token:
        print(f"expected inspect token {itr.token} to match created token {token}")
    if itr.generation_policy.id != GenerationPolicyUUID.id:
        print(f"expected inspect generation policy {itr.generation_policy.id} to match created generation policy {GenerationPolicyUUID.id}")
    if itr.access_policy.id != AccessPolicyOpen.id:
        print(f"expected inspect access policy {itr.access_policy.id} to match created access policy {AccessPolicyOpen.id}")

    try:
        if not c.DeleteToken(token):
            print("failed to delete token but no error?")
    except Error as e:
        print("failed to delete token: ", e)


def test_error_handling(c):
    try:
        d = c.ResolveToken("not a token", {})
        print("expected error but got data: ", d)
    except Error as e:
        if e.code != 404:
            print("got unexpected error code (wanted 404): ", e.code)


if __name__ == '__main__':
    c = Client(url, client_id, client_secret)

    test_access_policies(c)
    test_generation_policies(c)
    test_token_apis(c)
    test_error_handling(c)
