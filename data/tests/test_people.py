import pytest

import data.people as ppl
from unittest.mock import patch

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
    ppl.delete_person(_id)


def test_read_one(temp_person):
    assert ppl.read_one(temp_person) is not None

@pytest.mark.skip(reason="Skip for high performance reasons")
def test_get_masthead():
    mh = ppl.get_masthead()
    assert isinstance(mh, dict)


def test_get_mh_fields():
    flds = ppl.get_mh_fields()
    assert isinstance(flds, list)
    assert len(flds) > 0


def test_create_mh_rec(temp_person):
    person_rec = ppl.read_one(temp_person)
    mh_rec = ppl.create_mh_rec(person_rec)
    assert isinstance(mh_rec, dict)
    for field in ppl.MH_FIELDS:
        assert field in mh_rec


def test_has_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert ppl.has_role(person_rec, TEST_ROLE_CODE)


def test_doesnt_have_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert not ppl.has_role(person_rec, 'Not a good role!')


def test_is_valid_email_no_at():
    assert not ppl.is_valid_email(NO_AT)


def test_is_valid_no_name():
    assert not ppl.is_valid_email(NO_NAME)


def test_is_valid_no_domain():
    assert not ppl.is_valid_email(NO_DOMAIN)


def test_is_valid_email_domain_too_short():
    assert not ppl.is_valid_email(DOMAIN_TOO_SHORT)


def test_is_valid_email_domain_too_long():
    assert not ppl.is_valid_email(DOMAIN_TOO_LONG)


ADD_EMAIL = 'joe@nyu.edu'
@patch('data.people.read')
@patch('data.people.create', autospec=True)
def test_create(patch_create, patch_read):
    patch_create.return_value = ADD_EMAIL
    patch_read.return_value = {}

    people = ppl.read()
    assert ADD_EMAIL not in people
    ppl.create('Joe Smith', 'NYU', ADD_EMAIL, TEST_ROLE_CODE)
    patch_read.return_value = {ADD_EMAIL: {'name': 'Joe Smith',
                                           'affiliation': 'NYU',
                                           'email': ADD_EMAIL,
                                           'roles': [TEST_ROLE_CODE]}}

    people = ppl.read()
    assert ADD_EMAIL in people


def test_create_duplicate():
    with pytest.raises(ValueError):
        ppl.create('Do not care about name',
                   'Or affiliation', ppl.TEST_EMAIL, TEST_ROLE_CODE)

