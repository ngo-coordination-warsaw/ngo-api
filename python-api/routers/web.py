import fastapi
import typing


router = fastapi.APIRouter()

from models import Target, Listing, ListingType
from airtable import listings_table, labels_table


class LabelsContainer:
    def __init__(self) -> None:
        self.labels : dict()  # label_id -> label_data
        self.graph : dict()   # label_id -> children ids
        self.refresh()
        
    def refresh(self):
        # TODO: refresh sometimes
        self.labels = {'_root': {'id': '_root'}}
        self.graph  = dict()
        for record in labels_table.all():
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
    
def get_all_listings_visible_for_user() -> typing.List[Listing]:
    # TODO: access control
    records = listings_table.all(formula="_listingPublicVisibility")
    listings = [Listing.from_airtable_record(record) for record in records]
    return listings


@router.get('/listings', response_model=typing.List[Listing])
def get_listings(
    text_query: str = fastapi.Query(None, description='Not yet implemented'),  # TODO
    type: ListingType = fastapi.Query(None, description='(optional) only include needs or offers'),
    targets: typing.List[Target] = fastapi.Query([], description='(optional) consider only listings targeted at at least one of the provided "targets"'),
    labels_ids: typing.List[str] = fastapi.Query([], description='(optional) consider only listings with provided labels (or its sublabels) corresponding to provided labels ids, number of matched labels determines output order'),
    listings = fastapi.Depends(get_all_listings_visible_for_user)
):
    if type:
        listings = [listing for listing in listings if listing.type == type]
    
    if targets:
        listings = [listing for listing in listings if any(listing_target in targets for listing_target in listing.targets)]
    
    if labels_ids:
        labels_to_match_against = [        
            sublabel_id
            for selected_label_id in labels_ids
            for sublabel_id in labels_container.get_all_sublabels_ids(selected_label_id)
        ]
        
        def how_many_labels_match(listing, labels_to_match_against):
            n = 0
            for label in listing.labels_ids:
                if label in labels_to_match_against:
                    n += 1
            return n

        items = [
            {
                'n': how_many_labels_match(listing, labels_to_match_against),
                'listing': listing
            }
            for listing in listings
        ]

        items = [item for item in items if item['n'] > 0]
        items = sorted(items, reverse=True, key=lambda item: item['n'])
        listings = [item['listing'] for item in items]

    return listings