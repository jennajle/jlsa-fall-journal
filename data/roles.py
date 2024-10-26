
"""
This module manages person roles for a journal.
"""
from copy import deepcopy

AUTHOR_CODE = 'AU'
TEST_CODE = AUTHOR_CODE
ED_CODE = 'ED'
ME_CODE = 'ME'
CE_CODE = 'CE'
RE_CODE = 'RE'

ROLES = {
    AUTHOR_CODE: {'name': 'Author', 'description': 'Writes articles'},
    CE_CODE: {'name': 'Consulting Editor', 'description': 'Provides editorial consulting'},
    ED_CODE: {'name': 'Editor', 'description': 'Oversees the editorial process'},
    ME_CODE: {'name': 'Managing Editor', 'description': 'Manages editorial operations'},
    RE_CODE: {'name': 'Referee', 'description': 'Reviews submissions'},
}

MH_ROLES = [CE_CODE, ED_CODE, ME_CODE]


def get_roles() -> dict:
    return deepcopy(ROLES)


def get_masthead_roles() -> dict:
    return {code: role for code, role in ROLES.items() if 'Editor' in role['name']}


def get_role_codes() -> list:
    return list(ROLES.keys())


def is_valid(code: str) -> bool:
    return code in ROLES

def validate_roles(roles: list[str]) -> None:
    invalid_roles = [role for role in roles if role not in ROLES]
    if invalid_roles:
        raise ValueError(f"Invalid roles: {invalid_roles}")
    
def main():
    print(get_roles())
    print(get_masthead_roles())


if __name__ == '__main__':
    main()
