from http.client import (
    BAD_REQUEST, # 400
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND, # 404
    OK, # 200
    SERVICE_UNAVAILABLE,
    CREATED, # 201
)

from unittest.mock import patch

import pytest

import server.endpoints as ep

import data.manuscripts as manu
from data.people import NAME

TEST_CLIENT = ep.app.test_client()

PEOPLE_LOC = 'data.people.'


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    resp_json = resp.get_json()
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)
    assert len(resp_json[ep.TITLE_RESP]) > 0
    # print(f'{ep.TITLE_EP}')
    # print(f'{resp_json=}')

def test_get_people():
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    resp_json= resp.get_json()

    if resp.status_code == OK:
        assert isinstance(resp_json, dict)
        assert len(resp_json) > 0
    elif resp.status_code == NOT_FOUND:
        assert "Message" in resp_json
        assert resp_json["Message"] == "No people found in the database."
    else:
        assert False, f"Unexpected status code: {resp.status_code}"

def test_create_person():
    valid_person_data = {
        'name': 'John Doe',
        'role': 'AU',
        'affiliation': 'NYU',
        'email': 'johndoe@nyu.edu'
    }

    resp = TEST_CLIENT.post(ep.PEOPLE_EP, json=valid_person_data)
    resp_json = resp.get_json()
    assert resp.status_code == CREATED
    assert 'Person created successfully' in resp_json['Message']


@patch('data.people.read_one',  autospec=True, return_value={
    'name': 'John Doe',
    'roles': ['AU'],
    'affiliation': 'NYU',
    'email': 'johndoe@nyu.edu'
})
@patch('data.people.add_role',  autospec=True)
def test_add_role(mock_add_role, mock_read_one):
    _id = "johndoe@nyu.edu"
    role = "Editor"

    resp = TEST_CLIENT.post(f"{ep.PEOPLE_EP}/{_id}/roles/{role}")
    assert resp.status_code == OK

    mock_read_one.assert_called_once_with(_id)
    mock_add_role.assert_called_once_with(_id, role)


@patch('data.people.read_one', autospec=True, return_value={
    'name': 'John Doe',
    'roles': ['AU'],
    'affiliation': 'NYU',
    'email': 'johndoe@nyu.edu'
})
@patch('data.people.remove_role', autospec=True)
def test_delete_role(mock_remove_role, mock_read_one):
    role = "AU"
    resp = TEST_CLIENT.delete(f"{ep.PEOPLE_EP}/johndoe@nyu.edu/roles/{role}")
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert f"Role {role} removed successfully" in resp_json['Message']

    mock_remove_role.assert_called_once_with('johndoe@nyu.edu', role)

def test_delete_person():
    existing_person = {
        'name': 'John Doe',
        'roles': ['AU'],
        'affiliation': 'NYU',
        'email': 'johndoe@nyu.edu'
    }

    resp = TEST_CLIENT.delete(f"{ep.PEOPLE_EP}/johndoe@nyu.edu")
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert 'Person deleted successfully' in resp_json['Message']

@patch(PEOPLE_LOC + 'read', autospec=True,
       return_value={'id': {NAME: 'Joe Schmoe'}})
def test_read(mock_read):
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person

@patch(PEOPLE_LOC + 'read_one', autospec=True,
       return_value={NAME: 'Joe Schmoe'})
def test_read_one(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == OK

@patch(PEOPLE_LOC + 'read_one', autospec=True, return_value=None)
def test_read_one_not_found(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == NOT_FOUND


@patch(PEOPLE_LOC + 'read', autospec=True, return_value={
    'joshsmith@nyu.edu': {
        'name': 'Josh Smith',
        'roles': ['AU'],
        'affiliation': 'NYU',
        'email': 'joshsmith@nyu.edu'
    },
    'stellaadams@nyu.edu': {
        'name': 'Stella Adams',
        'roles': ['AU'],
        'affiliation': 'NYU',
        'email': 'stellaadams@nyu.edu'
    }
})
@patch('data.roles.is_valid', autospec=True, return_value=True)
def test_get_people_with_specific_role(mock_is_valid, mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/roles/AU')
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert 'AU' in resp_json
    assert len(resp_json['AU']) == 2


@patch('data.roles.is_valid', autospec=True, return_value=False)
def test_get_people_with_invalid_role(mock_is_valid):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/roles/INVALID_ROLE')
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert 'Invalid role' in resp_json['Message']


@patch('data.manuscripts.handle_action', autospec=True,
       return_value='SOME STRING')
def test_handle_action(mock_read):
    resp = TEST_CLIENT.put(f'{ep.MANU_EP}/receive_action',
                           json={
                               manu.MANU_ID: 'some id',
                               manu.CURR_STATE: 'some state',
                               manu.ACTION: 'some action',
                           })
    assert resp.status_code == OK
