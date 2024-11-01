import pytest
import data.people as ppl

from data.roles import TEST_CODE as TEST_ROLE_CODE

NO_AT = 'jkajsd'
NO_NAME = '@kalsj'
NO_DOMAIN = 'kajshd@'
NO_SUB_DOMAIN = 'kajshd@com'
DOMAIN_TOO_SHORT = 'kajshd@nyu.e'
DOMAIN_TOO_LONG = 'kajshd@nyu.eedduu'

TEMP_EMAIL = 'temp_person@temp.org'

@pytest.fixture(scope='function')
def temp_person():
    _id = ppl.create_person({
        'name': 'John Doe',
        'roles': ['AU'],
        'affiliation': 'NYU',
        'email': TEMP_EMAIL
    })
    yield _id
    ppl.delete(_id)