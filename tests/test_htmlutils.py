import pytest
from bs4 import BeautifulSoup
from zwutils import htmlutils

def test_find_soup_parent():
    htmlstr = '''
    <table class="myclass otherclass">
    <thead></thead>
    <tbody>
        <tr><td id="a"></td></tr>
        <tr></tr>
    </tbody>
    </table>
    '''
    el = BeautifulSoup(htmlstr, features='lxml')
    el = el.find(id='a')
    r = htmlutils.find_soup_parent(el, tagnm='table')
    assert r and r.name == 'table'

    r = htmlutils.find_soup_parent(el, attrs={'class': 'myclass'})
    assert r and r.name == 'table'

    r = htmlutils.find_soup_parent(el, tagnm='table', attrs={'class': 'myclass'})
    assert r and r.name == 'table'
