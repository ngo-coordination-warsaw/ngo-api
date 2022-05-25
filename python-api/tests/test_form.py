from models import Organization, Listing
from routers.form import *
import random
import pytest
from requests.exceptions import HTTPError


def test_form_crud():
    organization = Organization(
        name=f"test org {int(100*random.random())}",
        descriptionEN="description",
        contactPerson="contact_person",
        contactPhone="contact_phone",
        contactEmail="contact_email",
        additionalContactInfo="additional_contact_info",
    )

    # org create
    created_organization = create_organization(organization, UserData(firebase_user_uid='test_user'))
    organizationId = created_organization.organizationId
    organization.organizationId = organizationId

    # org read
    _read_organization = read_organization(organizationId)
    assert organization == _read_organization

    # org update
    updated_description = "updated_description"
    organization.descriptionEN = updated_description
    updated_organization = update_organization(organizationId, organization)
    assert organization == updated_organization

    listing = Listing(
        organizationId=organizationId,
        needOrOfferDescriptionEN="description",
        type="Need",
        fromOrForWhom=["CWK"],
        labelsIds=[],
    )

    # listing create
    created_listing = create_listing(organizationId, listing)
    listingId = created_listing.listingId
    listing.listingId = listingId

    # listeing read
    _read_listing = read_listing(organizationId, listingId)
    assert listing == _read_listing

    # listing update
    updated_description = "updated_description"
    listing.needOrOfferDescriptionEN = updated_description
    updated_listing = update_listing(organizationId, listingId, listing)
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
