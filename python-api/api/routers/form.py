from fastapi import HTTPException, Depends, APIRouter
from models import Organization, Listing
from airtable import organizations_table, listings_table


router = APIRouter()


# utils


def organization_with_this_name_exists(organization_name: str):
    return len(organizations_table.all(formula=f'Name="{organization_name}"')) > 0


def verify_organization_ownership(organization_id: str):
    # TODO: raise HTTPException(403) if actor doesn't own org
    pass


def verify_listing_ownership(organization_id: str, listing_id: str):
    # TODO: raise HTTPException(403) accordingly
    pass


# org crud


@router.post("/organization")
def create_organization(organization: Organization):
    if organization_with_this_name_exists(organization.name):
        raise HTTPException(status_code=404, detail="Organization name is taken")
    created_airtable_record = organizations_table.create(
        organization.to_airtable_fields()
    )
    return created_airtable_record


@router.get(
    "/organization/{organization_id}",
    dependencies=[Depends(verify_organization_ownership)],
)
def read_organization(organization_id: str):
    airtable_record = organizations_table.get(organization_id)
    return airtable_record


@router.put(
    "/organization/{organization_id}",
    dependencies=[Depends(verify_organization_ownership)],
)
def update_organization(organization_id: str, updated_organization: Organization):
    # TODO: prohibit changing name to existing one
    updated_airtable_record = organizations_table.update(
        organization_id, updated_organization.to_airtable_fields()
    )
    return updated_airtable_record


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
)
def create_listing(organization_id: str, listing: Listing):
    listing.organization_id = organization_id
    data = listing.to_airtable_fields()
    created_airtable_record = listings_table.create(data)
    return created_airtable_record


@router.get(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[
        Depends(verify_organization_ownership),
        Depends(verify_listing_ownership),
    ],
)
def delete_listing(organization_id: str, listing_id: str):
    airtable_record = listings_table.get(listing_id)
    return airtable_record


@router.put(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[
        Depends(verify_organization_ownership),
        Depends(verify_listing_ownership),
    ],
)
def update_listing(organization_id: str, listing_id: str, updated_listing: Listing):
    updated_listing.listing_id = listing_id
    updated_listing.organization_id = organization_id
    updated_airtable_record = listings_table.update(
        listing_id, updated_listing.to_airtable_fields()
    )
    return updated_airtable_record


@router.delete(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[
        Depends(verify_organization_ownership),
        Depends(verify_listing_ownership),
    ],
)
def delete_listing(organization_id: str, listing_id: str):
    deletion_report = listings_table.delete(listing_id)
    return deletion_report
