import pydantic
import typing
import enum


def snake_case_to_spaced_capitalized(s):
    return ' '.join(word.capitalize() for word in s.split('_'))

def spaced_capitalized_to_snake_case(s):
    return '_'.join(word.lower() for word in s.split(' '))


class Organization(pydantic.BaseModel):
    
    organization_id: typing.Optional[str]
    
    name: str
    description: str
    
    contact_person: str
    contact_phone: str
    contact_email: str
    additional_contact_info: str
    
    org_public_visibility: bool = False
    org_for_other_orgs_visibility: bool = False
    gdpr_consent: bool = False

    def to_airtable_fields(self):
        return {snake_case_to_spaced_capitalized(k): v for k, v in self.dict().items() if k != 'organization_id'}

    @classmethod
    def from_airtable_record(cls, record):
        self = Organization.parse_obj({spaced_capitalized_to_snake_case(k): v for k, v in record['fields'].items()})
        self.organization_id = record['id']
        return self



class Target(str, enum.Enum):
    cwk = "CWK"
    ngo = "NGOs"
    ind = "Individual helpers"
    ref = "Refugees"
    ukr = "Entities on Ukraine"

LabelId = str

ListingType = typing.Literal["Need", "Offer"]

class Listing(pydantic.BaseModel):
    listing_id: typing.Optional[str]
    organization_id: str
    description: str
    type: ListingType
    targets: typing.List[Target]
    labels_ids: typing.List[str]

    def to_airtable_fields(self):
        return {
            "OrganizationName": [self.organization_id],
            "Need/offer description": self.description,
            "Type": self.type,
            "From/for whom": [target.value for target in self.targets],
            "Labels": self.labels_ids
        }

    @classmethod
    def from_airtable_record(cls, record):
        self = cls(
            listing_id      = record['id'],
            organization_id = record['fields']['OrganizationName'][0],
            description     = record['fields'].get('Need/offer description', ''),
            type            = record['fields']['Type'],
            targets         = [Target(target) for target in record['fields'].get('From/for whom', [])],
            labels_ids      = record['fields'].get('Labels', [])
        )
        return self