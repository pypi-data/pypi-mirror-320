import pytest

from bbf.atmosphere import get_airmass_extinction, ExtinctionSpectrum


@pytest.mark.parametrize('source', ['palomar', 'Palomar', 'buton', 'Buton'])
def test_atmosphere_ok(source):
    assert isinstance(
        get_airmass_extinction(source=source),
        ExtinctionSpectrum)


def test_atmosphere_bad():
    with pytest.raises(ValueError) as err:
        get_airmass_extinction('unexisting source')
    assert 'Did not provide valid airmass extinction model' in str(err)
