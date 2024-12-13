import re


TITLE = 'title'
AUTHOR = 'author'
AUTHOR_EMAIL = 'author_email'
STATE = 'state'
REFEREES = 'referees'
TEXT = 'text'
ABSTRACT = 'abstract'
HISTORY = 'history'
EDITOR = 'editor'
DISP_NAME = 'disp_name'

TEST_FLD_NM = TITLE
TEST_FLD_DISP_NM = 'Title'
AUTHOR_DISP_NAME = 'Author'
AUTHOR_EMAIL_DISP_NAME = 'random@nyu.edu'
STATE_DISP_NAME = 'State'
REFEREES_DISP_NAME = 'Referees'
TEXT_DISP_NAME = 'Text'
ABSTRACT_DISP_NAME = 'Abstract'
HISTORY_DISP_NAME = 'History'
EDITOR_DISP_NAME = 'Editor'


FIELDS = {
    TITLE: {
        DISP_NAME: TEST_FLD_DISP_NM,
    },
    AUTHOR: {
        DISP_NAME: AUTHOR_DISP_NAME,
    },
    AUTHOR_EMAIL: {
        DISP_NAME: AUTHOR_EMAIL_DISP_NAME,
    },
    STATE: {
        DISP_NAME: STATE_DISP_NAME,
    },
    REFEREES: {
        DISP_NAME: REFEREES_DISP_NAME,
    },
    TEXT: {
        DISP_NAME: TEXT_DISP_NAME,
    },
    ABSTRACT: {
        DISP_NAME: ABSTRACT_DISP_NAME,
    },
    HISTORY: {
        DISP_NAME: HISTORY_DISP_NAME,
    },
    EDITOR: {
        DISP_NAME: EDITOR_DISP_NAME,
    },
}


def get_flds() -> dict:
    return FIELDS


def get_fld_names() -> list:
    return FIELDS.keys()


def get_disp_name(fld_nm: str) -> dict:
    fld = FIELDS.get(fld_nm, '')
    return fld[DISP_NAME]


def validate_field_data(field_data: dict) -> bool:
    for field in field_data:
        if field not in FIELDS:
            raise ValueError(f"Unknown field: {field}")
    return True


EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
def validate_email(email: str) -> bool:
    """
    Validate email is in proper format
    """
    if not re.match(EMAIL_REGEX, email):
        raise ValueError(f"Invalid email format: {email}")
    return True


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()
