import data.roles as rls

from unittest.mock import patch
import data.people as ppl

def test_get_roles():
    roles = rls.get_roles()
    assert isinstance(roles, dict)
    assert len(roles) > 0
    for code, role in roles.items():
        assert isinstance(code,str)
        assert isinstance(role,str)


def test_get_masthead_roles():
    mh_roles = rls.get_masthead_roles()
    assert isinstance(mh_roles, dict)
    assert len(mh_roles) > 0
    for role in mh_roles:
        assert role in rls.MH_ROLES


def test_get_role_codes():
    codes = rls.get_role_codes()
    assert isinstance(codes, list)
    for code in codes:
        assert isinstance(code, str)


def test_is_valid():
    assert rls.is_valid(rls.TEST_CODE)


@patch("data.people.read_one", autospec=True)
def test_remove_role(mock_read_one):
    test_email = "bob@nyu.edu"
    test_role = "AU"
    mock_person = {
        "name": "Bob",
        "email": test_email,
        "roles": [test_role, "ED"],
        "affiliation": "NYU"
    }

    mock_read_one.return_value = mock_person
    ppl.remove_role(test_email, test_role)
    assert test_role not in mock_person["roles"]


@patch("data.people.read_one", autospec=True)
def test_clear_roles(mock_read_one):
    test_email = "bob@nyu.edu"
    test_roles = ["AU", "ED", "CE"]
    mock_person = {
        "name": "Bob",
        "email": test_email,
        "roles": test_roles,
        "affiliation": "NYU"
    }

    mock_read_one.return_value = mock_person
    ppl.clear_roles(test_email)
    assert all([role not in mock_person["roles"] for role in rls.get_roles()])
