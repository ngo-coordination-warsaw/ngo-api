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
    
    contactPerson: typing.Optional[str]
    contactPhone: typing.Optional[str]
    contactEmail: typing.Optional[str]
    additionalContactInfo: typing.Optional[str]
    
    orgPublicVisibility: bool = False
    orgForOtherOrgsVisibility: bool = False
    gdprConsent: bool = False

    @pydantic.validator('name')
    def name_non_empty(value):
        if len(value) == 0:
            raise ValueError('Please provide organization name')
        return value
    
    @pydantic.root_validator
    def some_description_provided(cls, values):
        if not any([
            values.get('descriptionPL'),
            values.get('descriptionEN'),
            values.get('descriptionUA')
        ]):
            raise ValueError('Please provide some description')
        return values

    @pydantic.root_validator
    def some_contact_details_provided(cls, values):
        if not any([
            values.get('contactPerson'),
            values.get('contactEmail'),
            values.get('contactPhone')
        ]):
            raise ValueError('Please provide some contact details')
        return values

    
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
    needOrOfferDescriptionPL: typing.Optional[str]
    needOrOfferDescriptionEN: typing.Optional[str]
    needOrOfferDescriptionUA: typing.Optional[str]

    listingContactPerson: typing.Optional[str]
    listingContactPhone: typing.Optional[str]
    listingContactEmail: typing.Optional[str]
    listingAdditionalContactInfo: typing.Optional[str]

    type: ListingType
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
        data['organizationId'] = data['organization'][0]
        data['labelsIds'] = data.setdefault('labels', [])
        del data['organization']
        del data['labels']
        self = cls.parse_obj(data)
        self.listingId = record['id']
        return self