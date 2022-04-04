import pydantic
import typing
import enum

ContactDetails = str

class Organization(pydantic.BaseModel):
    organization_id: typing.Optional[str]
    name: str
    description: str
    contact_details: ContactDetails
    visible_publicly: bool
    visible_for_others: bool
    gdpr_consent: bool

    def to_airtable_fields(self):
        return {
            "Name": self.name,
            "Description": self.description,
            "orgPublicVisibility": self.visible_publicly,
            "orgForOtherOrgsVisibility": self.visible_for_others,
            "GDPR": self.gdpr_consent,
        }

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