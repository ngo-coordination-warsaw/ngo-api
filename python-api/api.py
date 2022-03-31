# run with: `uvicorn api:app` or `uvicorn api:app [--reload]`
# hosts docs at localhost:8000/docs

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Literal, Optional
import pydantic
import enum
import pyairtable
import os


app = FastAPI()


base = pyairtable.Base(
    os.environ['AIRTABLE_API_KEY'],
    os.environ['AIRTABLE_BASE_ID'],
)
organizations_table = base.get_table("Organizations")
listings_table = base.get_table("Listings")


# Models

ContactDetails = str

class Organization(pydantic.BaseModel):
    organization_id: Optional[str]
    name: str  # unique ?
    description: str
    visible_publicly: bool
    visible_for_others: bool
    gdpr_consent: bool
    contact_details: ContactDetails

    def to_airtable_fields(self):
        return {
            "Name": self.name,
            "Description": self.description,
            "orgPublicVisibility": self.visible_publicly,
            "orgForOtherOrgsVisibility": self.visible_for_others,
            "GDPR": self.gdpr_consent,
        }

class Target(enum.Enum):
    cwk = "CWK"
    ngo = "NGOs"
    ind = "Individual helpers"
    ref = "Refugees"
    ukr = "Entities in Ukraine"

Label = str

class Listing(pydantic.BaseModel):
    listing_id: Optional[str]
    organization_id: str
    description: str
    type: Literal["Need", "Offer"]
    target: List[Target]
    # labels: List[Label] TODO

    def to_airtable_fields(self):
        return {
            "OrganizationName": [self.organization_id],
            "Need/offer description": self.description,
            "Type": self.type,
            "From/for whom": [target.value for target in self.target],
        }


# API


def organization_with_this_name_exists(organization_name: str):
    return len(organizations_table.all(formula=f'Name="{organization_name}"')) > 0


@app.post("/organization")
def create_organization(organization: Organization):
    if organization_with_this_name_exists(organization.name):
        raise HTTPException(status_code=404, detail="Organization name is taken")
    created_airtable_record = organizations_table.create(
        organization.to_airtable_fields()
    )
    return created_airtable_record


@app.get("/organization/{organization_id}")
def read_organization(organization_id: str):
    # TODO restrict access?
    airtable_record = organizations_table.get(organization_id)
    return airtable_record


def verify_organization_ownership(organization_id: str):
    # TODO: raise HTTPException(403) if actor shouldn't access org data
    pass


@app.put(
    "/organization/{organization_id}", dependencies=[Depends(verify_organization_ownership)]
)
def update_organization(organization_id: str, updated_organization: Organization):
    # TODO: prohibit changing name to existing one
    updated_airtable_record = organizations_table.update(
        organization_id, updated_organization.to_airtable_fields()
    )
    return updated_airtable_record


@app.post(
    "/organization/{organization_id}/listing",
    dependencies=[Depends(verify_organization_ownership)],
)
def create_listing(organization_id: str, listing: Listing):
    listing.organization_id = organization_id
    data = listing.to_airtable_fields()
    created_airtable_record = listings_table.create(data)
    return created_airtable_record


@app.get("/organization/{organization_id}/listing/{listing_id}")
def delete_listing(organization_id: str, listing_id: str):
    # TODO restrict access?
    airtable_record = listings_table.get(listing_id)
    return airtable_record


def verify_listing_ownership(organization_id: str, listing_id: str):
    # TODO: raise HTTPException(403) accordingly
    pass


@app.put(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[Depends(verify_organization_ownership), Depends(verify_listing_ownership)],
)
def update_listing(organization_id: str, listing_id: str, updated_listing: Listing):
    updated_listing.listing_id = listing_id
    updated_listing.organization_id = organization_id
    updated_airtable_record = listings_table.update(
        listing_id, updated_listing.to_airtable_fields()
    )
    return updated_airtable_record


@app.delete(
    "/organization/{organization_id}/listing/{listing_id}",
    dependencies=[Depends(verify_organization_ownership), Depends(verify_listing_ownership)],
)
def delete_listing(organization_id: str, listing_id: str):
    deletion_report = listings_table.delete(listing_id)
    return deletion_report
