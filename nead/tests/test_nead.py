import pytest

import nead.nead_io as nead

def test_csv_read():
    df = nead.read_nead("sample_csv.dsv")
    assert(df.attrs["__format__"] == "NEAD 1.0 UTF-8")

# def test_write():
#     None
