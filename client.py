import base64
import sys
import time
import uuid

import jwt
import requests

from models import AccessPolicy, GenerationPolicy, InspectTokenResponse
import ucjson

class Error(BaseException):
    def __init__(self, error='unspecified error', code=500, request_id=None):
        self.error = error
        self.code = code
        self.request_id = request_id


    def __repr__(self):
        return f"Error({self.error}, {self.code}, {self.request_id})"


    @staticmethod
    def from_json(j):
        return Error(j['error'], j['request_id'])


class Client:
    url: str
    client_id: str
    _client_secret: str

    _access_token: str


    def __init__(self, url, id, secret):
        self.url = url
        self.client_id = id
        self._client_secret = secret

        self._access_token = self._get_access_token()


    ### Generation Policies

    def CreateGenerationPolicy(self, generation_policy: GenerationPolicy):
        body = {
            "generation_policy": generation_policy.__dict__
        }

        j = self._post(f"{self.url}/tokenizer/policies/generation", data=ucjson.dumps(body))
        return GenerationPolicy.from_json(j.get('generation_policy'))


    def ListGenerationPolicies(self):
        j = self._get(f"{self.url}/tokenizer/policies/generation")

        policies = []
        for p in j:
            policies.append(GenerationPolicy.from_json(p))

        return policies


    # Note: Generation Policies are immutable, so no Update method is provided.

    def DeleteGenerationPolicy(self, id: uuid.UUID):
        return self._delete(f"{self.url}/tokenizer/policies/generation/{str(id)}")


    ### Access Policies

    def CreateAccessPolicy(self, access_policy: AccessPolicy) -> AccessPolicy | Error:
        body = {
            "access_policy": access_policy.__dict__
        }

        j = self._post(f"{self.url}/tokenizer/policies/access", data=ucjson.dumps(body))
        return AccessPolicy.from_json(j.get("access_policy"))


    def ListAccessPolicies(self):
        j = self._get(f"{self.url}/tokenizer/policies/access")

        policies = []
        for p in j:
            policies.append(AccessPolicy.from_json(p))

        return policies


    def UpdateAccessPolicy(self, access_policy: AccessPolicy):
        body = {
            "access_policy": access_policy.__dict__
        }

        j = self._put(f"{self.url}/tokenizer/policies/access/{access_policy.id}", data=ucjson.dumps(body))
        return AccessPolicy.from_json(j.get("access_policy"))


    def DeleteAccessPolicy(self, id: uuid.UUID, version: int):
        body = {
            "version": version
        }

        return self._delete(f"{self.url}/tokenizer/policies/access/{str(id)}", data=ucjson.dumps(body))


    ### Token Operations

    def CreateToken(self, data: str, generation_policy: GenerationPolicy, access_policy: AccessPolicy) -> str:
        body = {
            "data": data,
            "generation_policy": generation_policy.__dict__,
            "access_policy": access_policy.__dict__
        }

        j = self._post(f"{self.url}/tokenizer/tokens", data=ucjson.dumps(body))
        return j["data"]


    def ResolveToken(self, token: str, context: dict) -> str:
        body = {
            "token": token,
            "context": context
        }

        j = self._post(f"{self.url}/tokenizer/tokens/actions/resolve", data=ucjson.dumps(body))
        return j["data"]


    def DeleteToken(self, token: str) -> bool:
        body = {
            "token": token
        }

        return self._delete(f"{self.url}/tokenizer/tokens", data=ucjson.dumps(body))


    def InspectToken(self, token: str) -> InspectTokenResponse:
        body = {
            "token": token
        }

        j = self._post(f"{self.url}/tokenizer/tokens/actions/inspect", data=ucjson.dumps(body))
        return InspectTokenResponse.from_json(j)


    def LookupToken(self, data: str, generation_policy: GenerationPolicy, access_policy: AccessPolicy) -> [str]:
        body = {
            "data": data,
            "generation_policy": generation_policy.__dict__,
            "access_policy": access_policy.__dict__
        }

        j = self._post(f"{self.url}/tokenizer/tokens/actions/lookup", data=ucjson.dumps(body))
        return j["tokens"]

    ### Access token helpers


    def _get_access_token(self) -> str:
        # Encode the client ID and client secret
        authorization = base64.b64encode(bytes(f"{self.client_id}:{self._client_secret}", "ISO-8859-1")).decode("ascii")

        headers = {
            "Authorization": f"Basic {authorization}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = {
            "grant_type": "client_credentials"
        }

        # Note that we use requests directly here (instead of _post) because we don't
        # want to refresh the access token as we are trying to get it. :)
        r = requests.post(f"{self.url}/oidc/token", headers=headers, data=body)
        j = ucjson.loads(r.text)
        return j.get('access_token')


    def _refresh_access_token_if_needed(self):
        if self._access_token is None:
            return

        # TODO: this takes advantage of an implementation detail that we use JWTs for access tokens,
        # but we should probably either expose an endpoint to verify expiration time, or expect to
        # retry requests with a well-formed error, or change our bearer token format in time.
        if jwt.decode(self._access_token, options={"verify_signature": False}).get('exp') < time.time():
            self._access_token = self._get_access_token()


    def _get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self._access_token}"}


    ### Request helpers

    def _get(self, url, **kwargs) -> dict:
        self._refresh_access_token_if_needed()
        r = requests.get(url, headers=self._get_headers(), **kwargs)
        j = ucjson.loads(r.text)

        if r.status_code >= 400:
            e = Error.from_json(j)
            e.code = r.status_code
            raise e

        return j


    def _post(self, url, **kwargs) -> dict:
        self._refresh_access_token_if_needed()
        r = requests.post(url, headers=self._get_headers(), **kwargs)
        j = ucjson.loads(r.text)

        if r.status_code >= 400:
            e = Error.from_json(j)
            e.code = r.status_code
            raise e

        return j


    def _put(self, url, **kwargs) -> dict:
        self._refresh_access_token_if_needed()
        r = requests.put(url, headers=self._get_headers(), **kwargs)
        j = ucjson.loads(r.text)

        if r.status_code >= 400:
            e = Error.from_json(j)
            e.code = r.status_code
            raise e

        return j


    def _delete(self, url, **kwargs) -> bool:
        self._refresh_access_token_if_needed()
        r = requests.delete(url, headers=self._get_headers(), **kwargs)

        if r.status_code >= 400:
            j = ucjson.loads(r.text)
            e = Error.from_json(j)
            e.code = r.status_code
            raise e

        return r.status_code == 204
