import data.manuscripts.fields as flds

AUTHOR_REV = 'AUR'
COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
TEST_STATE = SUBMITTED

VALID_STATES = [
    AUTHOR_REV,
    COPY_EDIT,
    IN_REF_REV,
    REJECTED,
    SUBMITTED,
]



SAMPLE_MANU = {
    flds.TITLE: 'Short module import names in Python',
    flds.AUTHOR: 'jlsa',
    flds.REFEREES: [],
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
# for testing:
TEST_ACTION = ACCEPT

VALID_ACTIONS = [
    ACCEPT,
    ASSIGN_REF,
    DONE,
    REJECT,
]

# can redefine and append more valid actions later on
VALID_ACTIONS_FOR_STATE = {
    'SUB': ['ARF', 'REJ'],
    'REV': ['ACC', 'REJ'],
    'CED': [],
    'REJ': [],
}


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def sub_assign_ref(manu: dict) -> str:
    return IN_REF_REV


FUNC = 'f'

STATE_TABLE = {
    SUBMITTED: {
        ASSIGN_REF: {
            FUNC: lambda m: IN_REF_REV,
        },
        REJECT: {
            FUNC: lambda m: REJECTED,
        },
    },
    IN_REF_REV: {
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda m: AUTHOR_REV,
        },
    },
    AUTHOR_REV: {
    },
    REJECTED: {
    },
}



def get_valid_actions_by_state(state: str):
    valid_actions = STATE_TABLE[state].keys()
    print(f'{valid_actions=}')
    return valid_actions


def handle_action(curr_state, action, manuscript) -> str:
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Bad state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'{action} not available in {curr_state}')
    return STATE_TABLE[curr_state][action][FUNC](manuscript)


def add_to_history(manuscript: dict, curr_state: str, action: str, new_state: str):
    history = manuscript.setdefault('history', [])
    history.append({
        'from': curr_state,
        'action': action,
        'to': new_state,
    })


def main():
    print(handle_action(SUBMITTED, ASSIGN_REF, SAMPLE_MANU))
    print(handle_action(SUBMITTED, REJECT, SAMPLE_MANU))


if __name__ == '__main__':
    main()
