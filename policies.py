import uuid

from models import AccessPolicy, GenerationPolicy

# Note: these need to stay in sync with authz/constants.go
AccessPolicyOpen = AccessPolicy(id=uuid.UUID("1bf2b775-e521-41d3-8b7e-78e89427e6fe"))
GenerationPolicyUUID = GenerationPolicy(id=uuid.UUID("f5bce640-f866-4464-af1a-9e7474c4a90c"))
GenerationPolicyEmail = GenerationPolicy(id=uuid.UUID("0cedf7a4-86ab-450a-9426-478ad0a60faa"))
GenerationPolicyFullName = GenerationPolicy(id=uuid.UUID("b9bf352f-b1ee-4fb2-a2eb-d0c346c6404b"))
GenerationPolicySSN = GenerationPolicy(id=uuid.UUID("3f65ee22-2241-4694-bbe3-72cefbe59ff2"))
GenerationPolicyCreditCard = GenerationPolicy(id=uuid.UUID("618a4ae7-9979-4ee8-bac5-db87335fe4d9"))
