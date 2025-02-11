import data.manuscripts.fields as flds

ACTION = 'action'
AUTHOR = 'author'
CURR_STATE = 'curr_state'
DISP_NAME = 'disp_name'
MANU_ID = '_id'
REFEREE = 'referees'
REFEREES = 'referees'
TITLE = 'title'

TEST_ID = 'fake_id'
TEST_FLD_NM = TITLE
TEST_FLD_DISP_NM = 'Title'

FIELDS = {
    TITLE: {
        DISP_NAME: TEST_FLD_DISP_NM,
    },
}

# states
AUTHOR_REV = 'AUR'
COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
WITHDRAWN = 'WIT'
EDITOR_REV = 'ERV'
FORMATTING = "FMT"
PUBLISHED = "PUB"
TEST_STATE = SUBMITTED

VALID_STATES = [
    AUTHOR_REV,
    COPY_EDIT,
    IN_REF_REV,
    REJECTED,
    SUBMITTED,
    WITHDRAWN,
    EDITOR_REV,
    FORMATTING,
    PUBLISHED,
]



SAMPLE_MANU = {
    flds.TITLE: 'Short module import names in Python',
    flds.AUTHOR: 'jlsa',
    flds.REFEREES: [],
    'history': [] # track what states the manuscript went through
}

SAMPLE_MANU_W_REF = {
    flds.TITLE: 'Short module import names in Python',
    flds.AUTHOR: 'jlsa',
    flds.REFEREES: {'Some ref': {}},
    'history': [] # track what states the manuscript went through
}

def get_states() -> list:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# actions:
ACCEPT = 'ACC'
ASSIGN_REF = 'ARF'
DONE = 'DON'
REJECT = 'REJ'
DELETE_REF = 'DRF'
WITHDRAW = 'WIT'
ACCEPT_REV = 'AWR'
# for testing:
TEST_ACTION = ACCEPT

VALID_ACTIONS = [
    ACCEPT,
    ASSIGN_REF,
    DONE,
    REJECT,
    WITHDRAW,
    DELETE_REF,
]

def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def submitted(manu: dict):
    print(f"Manuscript '{manu[flds.TITLE]}' is SUBMITTED")
    manu['state'] = SUBMITTED
    add_to_history(manu, None, 'SUBMIT', SUBMITTED)
    return SUBMITTED

# "message": "Bad action: err=TypeError(\"handle_action() got multiple values for argument 'manu_id'\")"
def assign_ref(manu: dict, referee: str, extra=None) -> str:
    manu[REFEREES].append(referee)
    return IN_REF_REV


def delete_ref(manu: dict, referee: str) -> str:
    if len(manu[flds.REFEREES]) > 0:
        manu[flds.REFEREES].remove(referee)
    if len(manu[flds.REFEREES]) > 0:
        return IN_REF_REV
    else:
        return SUBMITTED


def accept(manu:dict, referee: str, extra=None):
    if referee not in manu[flds.REFEREES]:
        return IN_REF_REV
    manu[flds.REFEREES][referee]["verdict"] = "ACCEPT"
    return COPY_EDIT


def accept_with_revisions(manu:dict, referee: str):
    if referee not in manu[flds.REFEREES]:
        return IN_REF_REV
    manu[flds.REFEREES][referee]["verdict"] = "ACCEPT_W_REVISIONS" # editor has to accept??
    return AUTHOR_REV

FUNC = 'f'

COMMON_ACTIONS = {
    WITHDRAW: {
        FUNC: lambda **kwargs: WITHDRAWN,
    },
}

STATE_TABLE = {
    SUBMITTED: {
        ASSIGN_REF: {
            FUNC: assign_ref,
        },
        REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        **COMMON_ACTIONS,
    },
    IN_REF_REV: {
        ASSIGN_REF: {
            FUNC: assign_ref,
        },
        DELETE_REF: {
            FUNC: delete_ref,
        },
        REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        ACCEPT: {
            FUNC: accept,
        },
        ACCEPT_REV: {
            FUNC: accept_with_revisions,
        },
        **COMMON_ACTIONS,
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda **kwargs: AUTHOR_REV,
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REV: {
        **COMMON_ACTIONS,
    },
    REJECTED: {
        **COMMON_ACTIONS,
    },
    WITHDRAWN: {
        **COMMON_ACTIONS,
    },
    EDITOR_REV: {
        **COMMON_ACTIONS,
    },
    FORMATTING: {
        **COMMON_ACTIONS,
    },
    PUBLISHED: {
        **COMMON_ACTIONS,
    },
}



def get_valid_actions_by_state(state: str):
    valid_actions = STATE_TABLE[state].keys()
    print(f'{valid_actions=}')
    return valid_actions


def handle_action(manu_id, curr_state, action, **kwargs) -> str:
    kwargs['manu'] = SAMPLE_MANU
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Bad state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'{action} not available in {curr_state}')
    return STATE_TABLE[curr_state][action][FUNC](**kwargs)


def add_to_history(manuscript: dict, curr_state: str, action: str, new_state: str):
    history = manuscript.setdefault('history', [])
    history.append({
        'from': curr_state,
        'action': action,
        'to': new_state,
    })


def reset_history(manuscript: dict):
    manuscript['history'] = []
    print("History has been reset.")


def main():
    print(handle_action(TEST_ID, SUBMITTED, ASSIGN_REF, referee='Jack'))
    #print(handle_action(SUBMITTED, REJECT, SAMPLE_MANU))


if __name__ == '__main__':
    main()
