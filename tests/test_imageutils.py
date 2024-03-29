# -*- coding: utf-8 -*-
import pytest
from pathlib import Path
from PIL import Image
import hashlib

from zwutils import imageutils as util
from zwutils import fileutils

BASEPATH = Path('./tests/data/imageutils')
TEMPPATH = BASEPATH / 'tmp'

def setup_module():
    fileutils.rmdir(TEMPPATH)

def teardown_module():
    setup_module()

def test_image_base64():
    imgpth = str( BASEPATH / 'zhao.png' )
    img = Image.open(imgpth)
    img_str = util.image_to_base64(img)
    new_img = util.base64_to_image(img_str)
    # new_img.show()
    o = hashlib.md5()
    o.update(img_str)
    s = o.hexdigest()
    assert s ==  '980a310f2fcc3faa0eb228f593cc015f'

def test_image_concate():
    outpth = TEMPPATH/'out.jpg'
    util.image_concate(BASEPATH/'concate_1.jpg', BASEPATH/'concate_2.jpg', outpth=outpth, direction=util.HORIZONTAL)
    s = fileutils.md5(outpth)
    assert s == '177d7283c01434dbb4252b4e4c4f66ce'
    util.image_concate(BASEPATH/'concate_1.jpg', BASEPATH/'concate_2.jpg', outpth=outpth, direction=util.VERTICAL)
    s = fileutils.md5(outpth)
    assert s == 'c9301931876cd476c587ae812b6b3a5a'

def test_image_list_concate():
    outpth = TEMPPATH/'out.jpg'
    imgs = [BASEPATH/'concate_1.jpg', BASEPATH/'concate_2.jpg']
    util.image_list_concate(imgs, outpth=outpth, direction=util.HORIZONTAL)
    s = fileutils.md5(outpth)
    assert s == '177d7283c01434dbb4252b4e4c4f66ce'
    util.image_list_concate(imgs, outpth=outpth, direction=util.VERTICAL)
    s = fileutils.md5(outpth)
    assert s == 'c9301931876cd476c587ae812b6b3a5a'
