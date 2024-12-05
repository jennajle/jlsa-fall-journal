import data.manuscripts.fields as mflds

import pytest


def test_get_flds():
    assert isinstance(mflds.get_flds(), dict)


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
