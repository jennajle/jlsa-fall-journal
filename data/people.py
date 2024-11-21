"""
This module interfaces to our people data
"""
import re
import data.db_connect as dbc
import data.roles as rls

PEOPLE_COLLECT = 'people'
MIN_USER_NAME_LEN = 2
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'

TEST_EMAIL = 'jl12631@nyu.edu'
DEL_EMAIL = 'delete@nyu.edu'

TEST_PERSON_DICT = {
    TEST_EMAIL: {
        NAME: 'Jenna Le',
        ROLES: [rls.ED_CODE],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL,
    },
    DEL_EMAIL: {
        NAME: 'Sejuti Mannan',
        ROLES: [rls.CE_CODE],
        AFFILIATION: 'NYU',
        EMAIL: DEL_EMAIL,
    },
}

people_dict = TEST_PERSON_DICT

client = dbc.connect_db()
print(f'{client=}')


CHAR_OR_DIGIT = '[A-Za-z0-9]'
VALID_CHARS = '[A-Za-z0-9_.]'


def is_valid_email(email: str) -> bool:
    return re.fullmatch(f"{VALID_CHARS}+@{CHAR_OR_DIGIT}+"
                        + "\\."
                        + f"{CHAR_OR_DIGIT}"
                        + "{2,3}", email)


def is_valid_person(name: str, affiliation: str,
                    email: str,
                    role: str, roles: list = None) -> bool:
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid role: {role}')
    elif roles:
        for role in roles:
            if not rls.is_valid(role):
                raise ValueError(f'Invalid role: {role}')
    return True


def get_people():
    return people_dict


def read() -> dict:
    print('read() has been called')
    return people_dict


def read_one(email: str) -> dict:
    """
    Return a person record if email present in DB,
    else None
    """
    return people_dict.get(email)


def delete(email: str):
    print(f'{EMAIL=}, {email=}')
    return dbc.delete(PEOPLE_COLLECT, {EMAIL: email})


def create_person(form_data):
    people = get_people()
    email = form_data.get('email')
    new_id = email
    name = form_data.get('name')
    person_roles = form_data.get('roles', [])

    if email in TEST_PERSON_DICT:
        print("Person already exists")
        return None
    elif not is_valid_email(email):
        raise ValueError("Invalid Email:", email)

    for role in person_roles:
        if not rls.is_valid(role):
            raise ValueError("Bad Role:", role)

    people[new_id] = {
        NAME: name,
        ROLES: person_roles,
        AFFILIATION: form_data.get('affiliation', ''),
        EMAIL: email,
    }
    return people[new_id][EMAIL]


def update_person(form_data):
    people = get_people()
    email = form_data.get('email')
    new_id = email
    name = form_data.get('name')
    new_roles = form_data.get('roles', [])

    if email not in TEST_PERSON_DICT:
        print("Person does not exist yet!")
        return None
    elif not is_valid_email(email):
        raise ValueError("Invalid Email:", email)

    for role in new_roles:
        if not rls.is_valid(role):
            raise ValueError("Bad Role:", role)

    people[new_id] = {
        NAME: name,
        ROLES: new_roles,
        AFFILIATION: form_data.get('affiliation', ''),
        EMAIL: email,
    }
    return people[new_id]


def add_role(email: str, role: str):
    # Check for if person exists is in endpoints.py
    person = read_one(email)
    # Check if role exists
    if not rls.is_valid(role):
        raise ValueError(f"Invalid role: {role}")

    if role not in person[ROLES]:
        person[ROLES].append(role)
    return email


def remove_role(email: str, role: str):
    # Check for if person exists is in endpoints.py
    person = read_one(email)
    # Check if role exists
    if not rls.is_valid(role):
        raise ValueError(f"Invalid role: {role}")
    # Check if person is assigned role
    if role not in person[ROLES]:
        raise ValueError(f"Role {role} is not assigned to email {email}")

    person[ROLES].remove(role)
    return email


def has_role(person: dict, role: str) -> bool:
    if role in person.get(ROLES):
        return True
    return False


MH_FIELDS = [NAME, AFFILIATION]


def get_mh_fields(journal_code=None) -> list:
    return MH_FIELDS


def create_mh_rec(person: dict) -> dict:
    mh_rec = {}
    for field in get_mh_fields():
        mh_rec[field] = person.get(field, '')
    return mh_rec


def get_masthead() -> dict:
    masthead = {}
    masthead_roles = rls.get_masthead_roles()
    people_data = read()

    for role_code, role_name in masthead_roles.items():
        people_with_role = [
            create_mh_rec(person)
            for _id, person in people_data.items()
            if has_role(person, role_code)
        ]
        masthead[role_name] = people_with_role

    return masthead


def create(name: str, affiliation: str, email: str, role: str):
    if is_valid_person(name, affiliation, email, role):
        roles = []
        if role:
            roles.append(role)
        person = {NAME: name, AFFILIATION: affiliation,
                  EMAIL: email, ROLES: roles}
        print(person)
        dbc.create(PEOPLE_COLLECT, person)
    return email


def main():
    print(get_masthead())


if __name__ == '__main__':
    main()
