# -*- coding: utf-8 -*-
from os import read
import pytest

from zwutils.fileutils import readjson
from zwutils.geoutils import *

@pytest.mark.parametrize(
    's, r', (
        ('浙江省国民经济和社会发展统计公报', 330000),
        ('北京市昌平区国民经济和社会发展统计公报', 110114),
        ('浙江省温州市鹿城区国民经济和社会发展统计公报', 330302),
        
    )
)
def test_address2adcode(s, r):
    codes = readjson('./data/codetree.json')
    o = address2adcode(s, codes)
    assert o == r
