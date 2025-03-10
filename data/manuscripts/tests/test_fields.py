import data.manuscripts.fields as mflds

import pytest

mflds.FIELDS = {
    mflds.TITLE: {mflds.DISP_NAME: "Title"},
    mflds.AUTHOR: {mflds.DISP_NAME: "Author"},
    mflds.AUTHOR_EMAIL: {mflds.DISP_NAME: "Author Email"},
    mflds.STATE: {mflds.DISP_NAME: "State"},
    mflds.REFEREES: {mflds.DISP_NAME: "Referees"},
    mflds.TEXT: {mflds.DISP_NAME: "Text"},
    mflds.ABSTRACT: {mflds.DISP_NAME: "Abstract"},
    mflds.HISTORY: {mflds.DISP_NAME: "History"},
    mflds.EDITOR: {mflds.DISP_NAME: "Editor"},
}


def test_get_flds():
    assert isinstance(mflds.get_flds(), dict)


def test_get_fld_names():
    expected_field_names = mflds.FIELDS.keys()
    assert list(mflds.get_fld_names()) == list(expected_field_names)


def test_flds_structure():
    fields = mflds.get_flds()
    assert isinstance(fields, dict)
    assert mflds.TITLE in fields
    assert mflds.DISP_NAME in fields[mflds.TITLE]
    assert fields[mflds.TITLE][mflds.DISP_NAME] == mflds.TEST_FLD_DISP_NM


def test_missing_disp_name():
    mflds.FIELDS['test_field'] = {}
    with pytest.raises(KeyError):
        mflds.get_disp_name('test_field')
    del mflds.FIELDS['test_field']


def test_empty_fields():
    """
    Clears fields dictionary to test
    behavior when empty, then restores.
    """
    original_fields = mflds.FIELDS.copy()
    mflds.FIELDS.clear()
    assert mflds.get_flds() == {}
    assert list(mflds.get_fld_names()) == []
    mflds.FIELDS.update(original_fields)


@pytest.mark.parametrize("fld_name, expected_disp_name", [
    (mflds.TITLE, mflds.TEST_FLD_DISP_NM),
])
def test_get_disp_name_parametrized(fld_name, expected_disp_name):
    assert mflds.get_disp_name(fld_name) == expected_disp_name


def test_validate_field_data_valid():
    valid_data = {
        mflds.TITLE: "Harry Potter Philosopher's Stone",
        mflds.AUTHOR: "Harry",
        mflds.AUTHOR_EMAIL: "harrypotter@gmail.com",
        mflds.STATE: "SUBMITTED",
        mflds.REFEREES: ["Ron", "Hermione"],
        mflds.TEXT: "Voldemort is returning.",
        mflds.ABSTRACT: "Abstract about manuscript.",
        mflds.HISTORY: [{"from": "SUBMITTED", "action": "REVIEW", "to": "IN_REF_REV"}], # specified in add_to_history
        mflds.EDITOR: "hagrid@gmail.com",
    }
    assert mflds.validate_field_data(valid_data) is True


def test_validate_field_data_invalid():
    invalid_data = {
        mflds.TITLE: "The Great Gatsby",
        "invalid_field": "random"
    }
    with pytest.raises(ValueError):
        mflds.validate_field_data(invalid_data)