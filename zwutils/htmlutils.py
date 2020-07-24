import re

def replace_all_space(s):
    return s.strip().replace(' ', '').replace('\xa0', '').replace('\u3000', '')

def find_soup_parent(el, tagnm=None, attrs=None):
    if isinstance(el, str) and not tagnm and not attrs:
        return None
    prt = el.parent
    rtn = None
    while prt and prt.name != 'body':
        pnm = False
        pat = False
        if tagnm and prt.name == tagnm:
            pnm = True
        if attrs and hasattr(prt, 'attrs'):
            for p in attrs:
                _t = prt.attrs[p] if p in prt.attrs else None
                _t = ' '.join(_t) if isinstance(_t, list) else _t
                if _t and len( re.findall(attrs[p], _t) )>0:
                    pat = True
        if tagnm and attrs and pnm and pat:
            rtn = prt
            break
        elif tagnm and pnm:
            rtn = prt
            break
        elif attrs and pat:
            rtn = prt
            break
        if not prt.parent:
            break
        prt = prt.parent
    return rtn
                

