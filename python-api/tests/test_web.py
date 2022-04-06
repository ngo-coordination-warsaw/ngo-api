from functools import partial
from models import Target


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_listings():
    def test(**kwargs):
        client.get('/listings', params=kwargs).raise_for_status()
    
    test()
    test(text_query='abc')
    test(type='Offer')
    test(targets=[Target.cwk])
    test(targets=[Target.cwk, Target.ngo])
    test(labels_ids=['labelId'])