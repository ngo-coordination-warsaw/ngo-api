import fastapi
import typing


router = fastapi.APIRouter()

from models import Target, Listing, ListingType
from airtable import listings_table, labels_table
from dependecies import get_web_user_access_level, AccessLevel
import airtable

class LabelsContainer:
    def __init__(self) -> None:
        self.labels : dict()  # label_id -> label_data
        self.graph : dict()   # label_id -> children ids
        self.refresh()
        
    def refresh(self):
        self.labels = {'_root': {'id': '_root'}}
        self.graph  = dict()
        for record in airtable.base.get_table('labels2').all():
            label = {
                'id': record['id'],
                'level': record['fields']['level'],
                'slug': record['fields']['slug'],
                'namePL': record['fields'].get('namePL'),
                'nameENG': record['fields'].get('nameENG'),
            }
            label_id = record['id']
            parent_id = record['fields']['parent'][0] if 'parent' in record['fields'] else '_root'
            
            self.labels[label_id] = label
            self.graph.setdefault(parent_id, set()).add(label_id)

    def get_labels_subtree(self, root_label_id='_root'):
        children_labels_ids = self.graph.get(root_label_id, [])
        return dict(
            **self.labels[root_label_id],
            children = [
                self.get_labels_subtree(child_label_id)
                for child_label_id in children_labels_ids
            ]
        )

    def get_all_sublabels_ids(self, root_label_id='_root'):
        children_labels_ids = self.graph.get(root_label_id, [])
        return sum(
            [
                self.get_all_sublabels_ids(child_label_id)
                for child_label_id in children_labels_ids
            ],
            start=[root_label_id]
        )

labels_container = LabelsContainer()


@router.get('/labels_tree')
def get_labels():
    return labels_container.get_labels_subtree()
    
def _get_listings(user_accces_level = fastapi.Depends(get_web_user_access_level)) -> typing.List[Listing]:
    if user_accces_level <= AccessLevel.PUBLIC:
        records = listings_table.all(formula="_listingPublicVisibility")
    elif user_accces_level <= AccessLevel.MEMBER_OF_VERIFIED_ORG:
        records = listings_table.all(formula="_listingForVerifiedUsersVisibility")
    elif user_accces_level <= AccessLevel.ADMIN:
        records = listings_table.all()
    else:
        raise PermissionError
    return [Listing.from_airtable_record(record) for record in records]


@router.get('/listings', response_model=typing.List[Listing])
def get_listings(
    text_query: str = None,  # TODO
    type: ListingType = None,
    targets: typing.List[Target] = fastapi.Query([]),
    labels_ids: typing.List[str] = fastapi.Query([]),
    listings = fastapi.Depends(_get_listings)
):
    if type:
        listings = [listing for listing in listings if listing.type == type]
    
    if targets:
        listings = [listing for listing in listings if any(listing_target in targets for listing_target in listing.targets)]
    
    if labels_ids:
        matching_labels = [        
            sublabel_id
            for selected_label_id in labels_ids
            for sublabel_id in labels_container.get_all_sublabels_ids(selected_label_id)
        ]
        
        def how_many_labels_match(listing, matching_labels):
            n = 0
            for label in listing.labels_ids:
                if label in matching_labels:
                    n += 1
            return n

        items = [
            {
                'n': how_many_labels_match(listing, matching_labels),
                'listing': listing
            }
            for listing in listings
        ]

        items = [item for item in items if item['n'] > 0]
        items = sorted(items, reverse=True, key=lambda item: item['n'])
        listings = [item['listing'] for item in items]

    return listings
