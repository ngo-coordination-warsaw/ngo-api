import pydantic
import typing
import enum


def snake_case_to_spaced_capitalized(s):
    return ' '.join(word.capitalize() for word in s.split('_'))

def spaced_capitalized_to_snake_case(s):
    return '_'.join(word.lower() for word in s.split(' '))


class Organization(pydantic.BaseModel):
    
    organizationId: typing.Optional[str]
    
    name: str
    description: str
    
    contactPerson: str
    contactPhone: str
    contactEmail: str
    additionalContactInfo: str
    
    orgPublicVisibility: bool = False
    orgForOtherOrgsVisibility: bool = False
    gdprConsent: bool = False

    def to_airtable_fields(self):
        data = self.dict()
        del data['organizationId'] 
        return data

    @classmethod
    def from_airtable_record(cls, record):
        self = cls.parse_obj(record['fields'])
        self.organizationId = record['id']
        return self


class Target(str, enum.Enum):
    cwk = "CWK"
    ngo = "NGOs"
    ind = "Individual helpers"
    ref = "Refugees"
    ukr = "Entities on Ukraine"


ListingType = typing.Literal["Need", "Offer"]

class Listing(pydantic.BaseModel):
    listingId: typing.Optional[str]
    organizationId: str
    needOrOfferDescription: str
    type: ListingType
    fromOrForWhom: typing.List[Target]
    labelsIds: typing.List[str]

    def to_airtable_fields(self):        
        data = self.dict()
        del data['listingId']
        del data['organizationId']
        data['organization'] = [self.organizationId]
        del data['labelsIds']
        data['labels'] = self.labelsIds
        return data

    @classmethod
    def from_airtable_record(cls, record):
        data = record['fields']
        data['organizationId'] = data['organization'][0]
        data['labelsIds'] = data.setdefault('labels', [])
        del data['organization']
        del data['labels']
        self = cls.parse_obj(data)
        self.listingId = record['id']
        # (
        #     listing_id      = record['id'],
        #     organization_id = record['fields']['OrganizationName'][0],
        #     description     = record['fields'].get('Need/offer description', ''),
        #     type            = record['fields']['Type'],
        #     targets         = [Target(target) for target in record['fields'].get('From/for whom', [])],
        #     labels_ids      = record['fields'].get('Labels', [])
        # )
        return self