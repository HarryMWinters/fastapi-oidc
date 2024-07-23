# type: ignore
import pydantic
import pytest

from fastapi_oidc import types


def test_IDToken_raises_with_bad_field_types():
    with pytest.raises(pydantic.ValidationError):
        types.IDToken(
            iss="ClearAirTurbulence",
            sub="ValueJudgement",
            aud="SoberCounsel",
            exp="NowTurningToReason&ItsJustSweetness",
            iat="GermaneRiposte",
        )


def test_IDToken_only_requires_fields_in_OIDC_spec():
    # Call IDToken with minimal types defined in spec
    assert types.IDToken(
        iss="ClearAirTurbulence",
        sub="ValueJudgement",
        aud="SoberCounsel",
        exp=3,
        iat=42,
    )


def test_IDToken_takes_arbitrary_extra_fields():
    assert types.IDToken(
        iss="ClearAirTurbulence",
        sub="ValueJudgement",
        aud="SoberCounsel",
        exp=3,
        iat=42,
        arbitrary_extra_field="Laskuil-Hliz",
    )
