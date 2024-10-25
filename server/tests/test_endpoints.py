from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

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
    assert isinstance(resp_json, dict)
    assert resp.status_code == 200 # server has successfully processed request

def test_create_person():
    valid_person_data = {
        'name': 'John Doe',
        'roles': ['AU'],
        'affiliation': 'NYU',
        'email': 'johndoe@nyu.edu'
    }

    resp = TEST_CLIENT.post(ep.PEOPLE_EP, json=valid_person_data)
    resp_json = resp.get_json()
    assert resp.status_code == 201  # Success
    assert 'Person created successfully' in resp_json['Message']

def test_delete_person():
    existing_person = {
        'name': 'John Doe',
        'roles': ['AU'],
        'affiliation': 'NYU',
        'email': 'johndoe@nyu.edu'
    }

    resp = TEST_CLIENT.delete(f"{ep.PEOPLE_EP}/johndoe@nyu.edu")
    resp_json = resp.get_json()
    assert resp.status_code == 200
    assert 'Person deleted successfully' in resp_json['Message']
