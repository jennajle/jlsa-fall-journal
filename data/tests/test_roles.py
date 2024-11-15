import data.roles as rls

from unittest.mock import patch

def test_get_roles():
    roles = rls.get_roles()
    assert isinstance(roles, dict)
    assert len(roles) > 0
    for code, role in roles.items():
        assert isinstance(code,str)
        assert isinstance(role,str)


@patch('data.roles.get_masthead_roles',  autospec=True)
def test_get_masthead_roles(patch_get_masthead_roles):
    patch_get_masthead_roles.return_value = {"CE": "Consulting Editor",
                                             "ED": "Editor",
                                             "ME": "Managing Editor"}

    mh_roles = rls.get_masthead_roles()
    assert isinstance(mh_roles, dict)
    assert patch_get_masthead_roles.called
    patch_get_masthead_roles.assert_called_once()


def test_get_role_codes():
    codes = rls.get_role_codes()
    assert isinstance(codes, list)
    for code in codes:
        assert isinstance(code, str)


def test_is_valid():
    assert rls.is_valid(rls.TEST_CODE)
