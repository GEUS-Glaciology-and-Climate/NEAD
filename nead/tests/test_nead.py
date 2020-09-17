import pytest

import nead.nead_io as nead

def test_read():
    # df = nead.read_dsv("https://raw.githubusercontent.com/mankoff/NEAD/main/sample.dsv")
    df = nead.read_dsv("sample.dsv")
    assert(df.attrs["__format__"] == "NEAD 1.0 UTF-8")

# def test_write():
#     None
