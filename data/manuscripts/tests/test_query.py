import random

import pytest

import data.manuscripts.query as mqry

from unittest.mock import patch


def gen_random_not_valid_str() -> str:
    """
    That huge number is only important in being huge:
        any big number would do.
    """
    BIG_NUM = 10_000_000_000
    big_int = random.randint(0, BIG_NUM)
    big_int += BIG_NUM
    bad_str = str(big_int)


@pytest.mark.parametrize("state", mqry.get_states())
def test_is_valid_state(state):
    assert mqry.is_valid_state(state)


def test_is_not_valid_state():
    # run this test "a few" times
    for i in range(10):
        assert not mqry.is_valid_state(gen_random_not_valid_str())


def test_is_valid_action():
    for action in mqry.get_actions():
        assert mqry.is_valid_action(action)


def test_is_not_valid_action():
    # run this test "a few" times
    for i in range(10):
        assert not mqry.is_valid_action(gen_random_not_valid_str())


def test_handle_action_bad_state():
    with pytest.raises(ValueError):
        mqry.handle_action(gen_random_not_valid_str(),
                           mqry.TEST_ACTION,
                           manu=mqry.SAMPLE_MANU)


def test_handle_action_bad_action():
    with pytest.raises(ValueError):
        mqry.handle_action(mqry.TEST_STATE,
                           gen_random_not_valid_str(),
                           manu=mqry.SAMPLE_MANU)


def test_handle_action_valid_return():
    for state in mqry.get_states():
        for action in mqry.get_valid_actions_by_state(state):
            print(f'{action=}')
            new_state = mqry.handle_action(state, action,
                                           manu=mqry.SAMPLE_MANU,
                                           ref='Some ref')
            print(f'{new_state=}')
            assert mqry.is_valid_state(new_state)


def test_handle_action_empty_inputs():
    with pytest.raises(ValueError):
        mqry.handle_action(curr_state="",
                           action=mqry.TEST_ACTION,
                           manu=mqry.SAMPLE_MANU)
    with pytest.raises(ValueError):
        mqry.handle_action(curr_state=mqry.TEST_STATE,
                           action="",
                           manu=mqry.SAMPLE_MANU)


def test_handle_action_no_state_change():
    for state in mqry.get_states():
        invalid_actions = [action for action in mqry.get_actions() if action not in mqry.get_valid_actions_by_state(state)]
        for action in invalid_actions:
            with pytest.raises(ValueError):
                mqry.handle_action(curr_state=state,
                                   action=action,
                                   manu=mqry.SAMPLE_MANU)


def test_handle_action_with_patch():
    with patch('data.manuscripts.query.handle_action', return_value=mqry.COPY_EDIT) as mock_handle_action:
        result = mqry.handle_action(mqry.IN_REF_REV, mqry.ACCEPT)
        mock_handle_action.assert_called_once_with(mqry.IN_REF_REV, mqry.ACCEPT)
        assert result == mqry.COPY_EDIT


@pytest.mark.parametrize(
    "curr_state, action, expected_state",
    [
        (mqry.SUBMITTED, mqry.ASSIGN_REF, mqry.IN_REF_REV),
        (mqry.SUBMITTED, mqry.REJECT, mqry.REJECTED),
    ],
)
def test_handle_action_valid_transitions(curr_state, action, expected_state):
    assert mqry.handle_action(curr_state=curr_state,
                              action=action,
                              manu=mqry.SAMPLE_MANU,
                              ref="Some ref") == expected_state


def test_invalid_transitions():
    invalid_combinations = [
        (mqry.COPY_EDIT, mqry.ASSIGN_REF),
        (mqry.REJECTED, mqry.ACCEPT),
        (mqry.IN_REF_REV, mqry.DONE),
    ]
    for state, action in invalid_combinations:
        with pytest.raises(ValueError):
            mqry.handle_action(curr_state=state,
                               action=action,
                               manu=mqry.SAMPLE_MANU)


def test_performance_large_inputs():
    states = [mqry.SUBMITTED for _ in range(10_000)]
    actions = [mqry.ASSIGN_REF for _ in range(10_000)]
    for state, action in zip(states, actions):
        assert mqry.handle_action(curr_state=state,
                                  action=action,
                                  manu=mqry.SAMPLE_MANU,
                                  ref="Some ref") == mqry.IN_REF_REV


@pytest.mark.parametrize(
    "state, expected_actions",
    [
        ('SUB', ['ARF', 'REJ', 'WIT']),
        ('REV', ['ARF', 'DRF', 'REJ', 'ACC', 'AWR', 'WIT']),
        ('CED', ['DON', 'WIT']),
        ('REJ', ['WIT']),
    ],
)
def test_get_valid_actions_by_state(state, expected_actions):
    assert list(mqry.get_valid_actions_by_state(state)) == expected_actions


def test_handle_action_with_mocked_manuscript():
    """
    Mock to make sure transitions only
    depend on curr_state and action
    """
    manuscript_mock = {
        "title": "Mock Title",
        "author": "Mock Author",
        "referees": {}
    }
    assert mqry.handle_action(curr_state=mqry.SUBMITTED,
                                  action=mqry.ASSIGN_REF,
                                  manu=manuscript_mock,
                                  ref="Mock ref") == mqry.IN_REF_REV


def test_withdraw_allowed_in_all_states():
    for state in mqry.STATE_TABLE.keys():
        assert mqry.WITHDRAW in mqry.get_valid_actions_by_state(state)


def test_accept_action_valid():
    curr_state, expected_state = 'REV', 'CED'
    new_state = mqry.handle_action(curr_state=curr_state,
                                    action=mqry.ACCEPT,
                                    manu=mqry.SAMPLE_MANU_W_REF,
                                    ref="Some ref")
    assert new_state == expected_state
    assert mqry.is_valid_state(new_state)

def test_accept_action_with_revisions_valid():
    curr_state, expected_state = 'REV', 'AUR'
    new_state = mqry.handle_action(curr_state=curr_state,
                                    action=mqry.ACCEPT_REV,
                                    manu=mqry.SAMPLE_MANU_W_REF,
                                    ref="Some ref")
    assert new_state == expected_state
    assert mqry.is_valid_state(new_state)


def test_reset_history():
    manuscript = {
        "history": [
            {"from": "SUB", "action": "ARF", "to": "REV"},
            {"from": "REV", "action": "ACC", "to": "CED"},
        ]
    }
    mqry.reset_history(manuscript)
    assert manuscript["history"] == []


def test_add_to_history_empty_history_field():
    manuscript = {}
    mqry.add_to_history(manuscript, curr_state="SUB", action="ARF", new_state="REV")
    assert "history" in manuscript
    assert manuscript["history"] == [{"from": "SUB", "action": "ARF", "to": "REV"}]

def test_add_to_history_multiple_entries():
    manuscript = {
        "history": [{"from": "SUB", "action": "ARF", "to": "REV"}]
    }
    mqry.add_to_history(manuscript, curr_state="REV", action="ACC", new_state="CED")
    assert manuscript["history"] == [
        {"from": "SUB", "action": "ARF", "to": "REV"},
        {"from": "REV", "action": "ACC", "to": "CED"}
    ]