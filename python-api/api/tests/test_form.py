from api.models import Organization, Listing
from api.routers.form import *
import random
import pytest
from requests.exceptions import HTTPError


def test_form_crud():
    organization = Organization(
        name=f"test org {int(100*random.random())}",
        description="description",
        contactPerson="contact_person",
        contactPhone="contact_phone",
        contactEmail="contact_email",
        additionalContactInfo="additional_contact_info",
    )

    # org create
    created_airtable_record = create_organization(organization)
    organizationId = created_airtable_record["id"]
    organization.organizationId = organizationId

    # org read
    airtable_record = read_organization(organizationId)
    _read_organization = Organization.from_airtable_record(airtable_record)
    assert organization == _read_organization

    # org update
    updated_description = "updated_description"
    organization.description = updated_description
    updated_airtable_record = update_organization(organizationId, organization)
    updated_organization = Organization.from_airtable_record(updated_airtable_record)
    assert organization == updated_organization

    listing = Listing(
        organizationId=organizationId,
        needOrOfferDescription="description",
        type="Need",
        fromOrForWhom=["CWK"],
        labelsIds=[],
    )

    # listing create
    created_airtable_record = create_listing(organizationId, listing)
    listingId = created_airtable_record["id"]
    listing.listingId = listingId

    # listeing read
    airtable_record = read_listing(organizationId, listingId)
    _read_listing = Listing.from_airtable_record(airtable_record)
    assert listing.dict() == _read_listing.dict()

    # listing update
    updated_description = "updated_description"
    listing.needOrOfferDescription = updated_description
    updated_airtable_record = update_listing(organizationId, listingId, listing)
    updated_listing = Listing.from_airtable_record(updated_airtable_record)
    assert listing == updated_listing

    # listing delete
    delete_listing(organizationId, listingId)
    with pytest.raises(HTTPError, match="404"):
        read_listing(organizationId, listingId)

    # org delete
    delete_organization(organizationId)
    with pytest.raises(HTTPError, match="404"):
        read_organization(organizationId)


def test_form_auth():
    pass
