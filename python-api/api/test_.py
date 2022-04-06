from api.models import Organization, Listing
from api.routers.form import *
import random
import pytest
from requests.exceptions import HTTPError


def test_form_crud():
    organization = Organization(
        name=f'test org {int(100*random.random())}',
        description='description',
        contact_person='contact_person',
        contact_phone='contact_phone',
        contact_email='contact_email',
        additional_contact_info='additional_contact_info',
    )

    # org create
    created_airtable_record = create_organization(organization)
    organization_id = created_airtable_record['id']
    organization.organization_id = organization_id

    # org read
    airtable_record = read_organization(organization_id)
    _read_organization = Organization.from_airtable_record(airtable_record)
    assert organization == _read_organization
    
    # org update
    updated_description = 'updated_description'
    organization.description = updated_description    
    updated_airtable_record = update_organization(organization_id, organization)
    updated_organization = Organization.from_airtable_record(updated_airtable_record)
    assert organization == updated_organization

    # listing create
    listing = Listing(
        organization_id=organization_id,
        need_or_offer_description='description',
        type='Need',
        from_or_for_whom=['CWK'],
        labels_ids=[]
    )

    # org delete
    delete_organization(organization_id)
    with pytest.raises(HTTPError, match="404"):
        read_organization(organization_id)

