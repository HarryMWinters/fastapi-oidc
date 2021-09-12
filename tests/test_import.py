import fastapi_oidc


def test_can_import_things_from_project_root():
    assert fastapi_oidc.types.IDToken
    assert fastapi_oidc.types.OktaIDToken
    assert fastapi_oidc.get_auth
