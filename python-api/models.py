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
    descriptionPL: typing.Optional[str]
    descriptionEN: typing.Optional[str]
    descriptionUA: typing.Optional[str]
    
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
    organizationId: typing.Optional[str]
    needOrOfferDescriptionPL: typing.Optional[str]
    needOrOfferDescriptionEN: typing.Optional[str]
    needOrOfferDescriptionUA: typing.Optional[str]

    listingContactPerson: typing.Optional[str]
    listingContactPhone: typing.Optional[str]
    listingContactEmail: typing.Optional[str]
    listingAdditionalContactInfo: typing.Optional[str]

    type: typing.Optional[ListingType]
    fromOrForWhom: typing.List[Target] = []
    labelsIds: typing.List[str] = []

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
        data['organizationId'] = data.setdefault('organization', [None])[0]
        data['labelsIds'] = data.setdefault('labels', [])
        del data['organization']
        del data['labels']
        self = cls.parse_obj(data)
        self.listingId = record['id']
        return self