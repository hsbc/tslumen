import pytest
from tests.functional.data import datasets

from tslumen.profile import features


@pytest.mark.parametrize(
    "fname,sname,ser",
    [(fname, s.name, s)
     for fname, df in datasets['features'].items()
     for _, s in df.items()]
)
def test_features(fname, sname, ser):
    ft = sname[:sname.rfind('=')]
    expected = float(sname[sname.rfind('=') + 1:])
    fn = getattr(features, fname)
    fts = fn(ser).result
    assert abs(expected-fts[ft]) < 0.05
