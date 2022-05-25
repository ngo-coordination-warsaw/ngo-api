from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPBearer
from models import Organization, Listing
from airtable import organizations_table, listings_table, users_table
from firebase import decode_jwt
import pydantic
import typing
import os


router = APIRouter()

# auth

scheme = HTTPBearer()

class UserData(pydantic.BaseModel):
    firebase_user_uid: str
    airtable_user_record_id: typing.Optional[str]
    organizationId: typing.Optional[str]
    listingsIds: typing.List[str] = []

def authorize_and_get_user_data(jwt: str = Depends(scheme)) -> UserData:
    
    firebase_user_data = decode_jwt(jwt.credentials)
    uid = firebase_user_data['uid']

    user_data = UserData(firebase_user_uid=uid)
    
    user_records = users_table.all(formula=f'firebaseUid="{uid}"')
    if len(user_records) >= 2:
        raise RuntimeError(f'More than one airtable user entry for {uid}!')
    elif len(user_records) == 1:
        user_record = user_records[0]
        user_data.airtable_user_record_id = user_record['id']
        user_data.organizationId = user_record.get('organization', [None])[0]

    if user_data.organizationId:
        organization_record = organizations_table.get(user_data.organizationId)
        user_data.listingsIds = organization_record['fields'].get('Listings', [])

    return user_data


def organization_with_this_name_exists(organization_name: str):
    return len(organizations_table.all(formula=f'Name="{organization_name}"')) > 0


def verify_organization_ownership(organization_id: str, user_data: UserData = Depends(authorize_and_get_user_data)):
    if os.environ.get('SKIP_OWNERSHIP_VERIFICATION', False):
        return
    if user_data.organizationId is None:
        raise HTTPException(status_code=404, detail=f"User does not own any org!")
    if user_data.organizationId != organization_id:
        raise HTTPException(status_code=403, detail=f"User does not own this org!")


def verify_listing_ownership(organization_id: str, listing_id: str, user_data: UserData = Depends(authorize_and_get_user_data)):
    if os.environ.get('SKIP_OWNERSHIP_VERIFICATION', False):
        return
    verify_organization_ownership(organization_id, user_data)
    if listing_id not in user_data.listingsIds:
        raise HTTPException(status_code=403, detail=f"This org does not own this listing!")


@router.post("/organization")
def create_organization(organization: Organization, user_data: UserData = Depends(authorize_and_get_user_data)):
    # 1. create org entry
    # 2. create user entry and assign org

    if user_data.organizationId:
        raise HTTPException(status_code=404, detail=f"User already owns org {user_data.organizationId}")
    if organization_with_this_name_exists(organization.name):
        raise HTTPException(status_code=404, detail="Organization name is taken")
    created_airtable_organization_record = organizations_table.create(
        organization.to_airtable_fields()
    )
    organization_id = created_airtable_organization_record['id']
    
    assign_org_to_user(organization_id, user_data.firebase_user_uid)
    
    return Organization.from_airtable_record(created_airtable_organization_record)

@router.post("/organization/{organization_id}/add_user", dependencies=[Depends(verify_organization_ownership)])
def assign_org_to_user(organization_id: str, firebase_uid: str):
    user_records = users_table.all(formula=f'firebaseUid="{firebase_uid}"')
    if len(user_records) >= 2:
        raise HTTPException(status_code=500, detail=f"Multiple DB entries for one user!")
    elif len(user_records) == 1:
        user_record = user_records[0]
        if user_record['fields'].get('organization', [None])[0]:
            raise HTTPException(status_code=500, detail=f"User already assigned to some org!")
        users_table.update(record_id=user_record['id'], fields={'organization': [organization_id]}, replace=False)
    else:
        created_user_record = users_table.create({
            'firebaseUid': firebase_uid,
            'organization': [organization_id]
        })

    return 

@router.get(
    "/organization/{organization_id}",
    dependencies=[Depends(verify_organization_ownership)],
    response_model = Organization
)
def read_organization(organization_id: str):
    airtable_record = organizations_table.get(organization_id)
    return Organization.from_airtable_record(airtable_record)


@router.put(
    "/organization/{organization_id}",
    dependencies=[Depends(verify_organization_ownership)],
    response_model = Organization
)
def update_organization(organization_id: str, updated_organization: Organization):
    # TODO: prohibit changing name to existing one
    updated_airtable_record = organizations_table.update(
        organization_id, updated_organization.to_airtable_fields()
    )
    return Organization.from_airtable_record(updated_airtable_record)


@router.delete(
    "/organization/{organization_id}",
    dependencies=[Depends(verify_organization_ownership)],
)
def delete_organization(organization_id: str):
    deletion_report = organizations_table.delete(organization_id)
    return deletion_report


# listings crud


@router.post(
    "/organization/{organization_id}/listing",
    dependencies=[Depends(verify_organization_ownership)],
    response_model=Listing
)
def create_listing(organization_id: str, listing: Listing):
    listing.organizationId = organization_id
    data = listing.to_airtable_fields()
    created_airtable_record = listings_table.create(data)
    return Listing.from_airtable_record(created_airtable_record)


@router.get(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[Depends(verify_listing_ownership)]
)
def read_listing(organization_id: str, listing_id: str):
    airtable_record = listings_table.get(listing_id)
    return Listing.from_airtable_record(airtable_record)

@router.get(
    "/organization/{organization_id}/all_listings",
    # TODO: access control dependencies=[Depends(verify_listing_ownership)]
)
def read_all_listings(organization_id: str):
    airtable_record = listings_table.all(formula=f'organizationId="{organization_id}"')
    return airtable_record


@router.put(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[Depends(verify_listing_ownership)]
)
def update_listing(organization_id: str, listing_id: str, updated_listing: Listing):
    updated_listing.listingId = listing_id
    updated_listing.organizationId = organization_id
    updated_airtable_record = listings_table.update(
        listing_id, updated_listing.to_airtable_fields()
    )
    return Listing.from_airtable_record(updated_airtable_record)


@router.delete(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[Depends(verify_listing_ownership)]
)
def delete_listing(organization_id: str, listing_id: str):
    deletion_report = listings_table.delete(listing_id)
    return deletion_report
