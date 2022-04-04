import enum
from fastapi import Depends
import fastapi.security

class AccessLevel(enum.IntEnum):
    PUBLIC = 1
    MEMBER_OF_VERIFIED_ORG = 2
    ADMIN = 3

auth_scheme = fastapi.security.APIKeyHeader(name='api_key')
def get_web_user_access_level(api_key = Depends(auth_scheme)):
    # TODO
    return AccessLevel.PUBLIC

def verify_organization_ownership(organization_id: str):
    # TODO: raise HTTPException(403) if actor doesn't own org
    pass

def verify_listing_ownership(organization_id: str, listing_id: str):
    # TODO: raise HTTPException(403) accordingly
    pass
