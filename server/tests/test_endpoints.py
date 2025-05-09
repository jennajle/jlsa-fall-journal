import sys
import os
# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

import server.endpoints as ep
from http import HTTPStatus
from unittest.mock import patch
import pytest

from http.client import (
    BAD_REQUEST, # 400
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND, # 404
    OK, # 200
    SERVICE_UNAVAILABLE,
    CREATED, # 201
)

import data.manuscripts as manu
from data.people import NAME

TEST_CLIENT = ep.app.test_client()
OK = HTTPStatus.OK
FORBIDDEN = HTTPStatus.FORBIDDEN

PEOPLE_LOC = 'data.people.'
from security.security import GOOD_USER_ID


# def test_hello():
#     resp = TEST_CLIENT.get(ep.HELLO_EP)
#     resp_json = resp.get_json()
#     assert ep.HELLO_RESP in resp_json


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
        assert len(resp_json) >= 0
    elif resp.status_code == NOT_FOUND:
        assert "Message" in resp_json
        assert resp_json["Message"] == "No people found in the database."
    else:
        assert False, f"Unexpected status code: {resp.status_code}"

def test_create_person():
    valid_person_data = {
        'name': 'John Doe',
        'role': ['AU'],
        'affiliation': 'NYU',
        'email': 'johndoe@nyu.edu',
        'password': 'password'
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

    resp = TEST_CLIENT.delete(f"/people/delete/{existing_person['email']}/{GOOD_USER_ID}")
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
    email = 'mock_id'
    user_id = GOOD_USER_ID
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/{email}')
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


# @patch('data.manuscripts.handle_action', autospec=True)
# def test_handle_action(mock_handle_action):
#     mock_handle_action.return_value = {"new_state": "WIT"}
#     resp = TEST_CLIENT.put(f'{ep.MANU_EP}/receive_action',
#                            json={
#                                manu.MANU_ID: '67c7700a985d03e678e4513e',
#                                manu.CURR_STATE: 'SUB',
#                                manu.ACTION: 'WIT',
#                                manu.REFEREE: 'some ref',
#                            })
#     assert resp.status_code == OK

@patch('data.people.read_one')
@patch('data.people.update')
def test_update_person_authorization(mock_update, mock_read_one):
    """Test authorization checks for updating person profiles"""
    # Test case 1: User trying to edit their own profile (should succeed)
    mock_read_one.side_effect = [
        {'name': 'John Doe', 'roles': ['AU'], 'email': 'john@example.com'},  # current_person
        {'name': 'John Doe', 'roles': ['AU'], 'email': 'john@example.com'}   # user
    ]
    mock_update.return_value = 'john@example.com'
    
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}?old_email=john@example.com&user_id=john@example.com",
        json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'roles': ['AU'],
            'affiliation': 'NYU'
        }
    )
    assert resp.status_code == OK
    assert 'Person updated successfully' in resp.json['Message']

    # Test case 2: Author trying to edit another person's profile (should fail)
    mock_read_one.side_effect = [
        {'name': 'Jane Smith', 'roles': ['AU'], 'email': 'jane@example.com'},  # current_person
        {'name': 'John Doe', 'roles': ['AU'], 'email': 'john@example.com'}     # user
    ]
    
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}?old_email=jane@example.com&user_id=john@example.com",
        json={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'roles': ['AU'],
            'affiliation': 'NYU'
        }
    )
    assert resp.status_code == FORBIDDEN
    assert 'You can only edit your own profile' in resp.json['Message']

    # Test case 3: Admin trying to edit another person's profile (should succeed)
    mock_read_one.side_effect = [
        {'name': 'Jane Smith', 'roles': ['AU'], 'email': 'jane@example.com'},  # current_person
        {'name': 'Admin User', 'roles': ['AD'], 'email': 'admin@example.com'}  # user
    ]
    mock_update.return_value = 'jane@example.com'
    
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}?old_email=jane@example.com&user_id=admin@example.com",
        json={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'roles': ['AU'],
            'affiliation': 'NYU'
        }
    )
    assert resp.status_code == OK
    assert 'Person updated successfully' in resp.json['Message']

    # Test case 4: Missing user_id (should fail)
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}?old_email=john@example.com",
        json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'roles': ['AU'],
            'affiliation': 'NYU'
        }
    )
    assert resp.status_code == FORBIDDEN
    assert 'User ID is required for authorization' in resp.json['Message']

    # Test case 5: Invalid user_id (should fail)
    mock_read_one.side_effect = [
        {'name': 'John Doe', 'roles': ['AU'], 'email': 'john@example.com'},  # current_person
        None  # user not found
    ]
    
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}?old_email=john@example.com&user_id=invalid@example.com",
        json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'roles': ['AU'],
            'affiliation': 'NYU'
        }
    )
    assert resp.status_code == FORBIDDEN
    assert 'Invalid user ID' in resp.json['Message']
