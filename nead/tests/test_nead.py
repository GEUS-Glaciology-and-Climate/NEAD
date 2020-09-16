import pytest

import nead.nead_io as nead

def test_read():
    # df = nead.read_dsv("https://raw.githubusercontent.com/mankoff/NEAD/main/sample.dsv")
    df = nead.read_dsv("sample.dsv")
    assert(df.attrs["format"] == "NEAD 0.1 ASCII")

# def test_write():
#     None
