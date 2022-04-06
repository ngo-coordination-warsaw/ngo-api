import pyairtable
import os


base = pyairtable.Base(
    os.environ['AIRTABLE_API_KEY'],
    os.environ['AIRTABLE_BASE_ID'],
)


organizations_table = base.get_table("Organizations")
listings_table = base.get_table("Listings")
labels_table = base.get_table("Labels")
