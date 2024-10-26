import data.roles as rls

def test_get_roles():
    roles = rls.get_roles()
    assert isinstance(roles, dict)
    assert len(roles) > 0
    for code, role in roles.items():
        
        assert isinstance(code,str)
        assert isinstance(role,str)
      
        assert 'name' in role
        assert 'description' in role
        assert 'can_edit' in role
        assert 'can_review' in role
        
        assert isinstance(role['name'], str)
        assert isinstance(role['description'], str)
        assert isinstance(role['can_edit'], bool)
        assert isinstance(role['can_review'], bool)