import re
import time
import platform
import subprocess
import logging
import requests
from pathlib import Path
from bs4 import BeautifulSoup

from zwutils.dlso import ZWObject, update_attrs
from zwutils.mthreading import ThreadPool
from zwutils.fileutils import readjson, writejson

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'

# [DEFAULT_CONFIG]
DEFAULT_CONFIG = {
    # [REQUEST_OPTION]
    'requests': {
        'headers': {'user-agent': DEFAULT_USER_AGENT},
        'cookies': None,
        'proxies': None,
        'timeout': 5,           # seconds, 连接超时设为比3的倍数略大的一个数值
    },
    'http_success_only': False,
    # [REQUEST_OPTION]

    # multithread_request options
    'thread_num': 5,
    'thread_timeout': 6,    # seconds

    # [COOKIES_OPTION]
    'cookiespath': None
    # [COOKIES_OPTION]
}
# [DEFAULT_CONFIG]

def get_request_kwargs(cfg=None, **kwargs):
    """This Wrapper method exists b/c some values in req_kwargs dict
    are methods which need to be called every time we make a request

    :meta private:
    """
    kv = kwargs.copy()
    cfg = ZWObject.from_dict(cfg) if cfg and isinstance(cfg, dict) else cfg
    # kwargs overwrite cfg.requests
    if hasattr(cfg, 'requests'):
        o = cfg.as_dict()['requests']
        for k,v in o.items():
            if k not in kv:
                kv[k] = v
    for key, val in kv.items():
        if callable(val):
            kv[key] = val()

    # default value
    kv['allow_redirects'] = kv.get('allow_redirects', True)
    kv['verify']  = kv.get('verify', False)
    kv['headers'] = kv.get('headers', {'user-agent': DEFAULT_USER_AGENT})
    kv['headers']['user-agent'] = kv['headers'].get('user-agent', DEFAULT_USER_AGENT)
    return kv

def ping(host):
    """Returns host ip if host (str) responds to a ping request or None if not.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    param = '-n' if platform.system().lower()=='windows' else '-c'
    cmd = ['ping', param, '1', host]
    r = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('latin')
    arr = re.findall(r'Ping.+\[(.*)\]', r)
    return arr[0] if arr else None

def head(url, cfg=None, params=None, json=None, data=None, **kwargs):
    """Send head request

    :return: :class:`Response <Response>` object
    :rtype: requests.Response

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :language: python
        :start-after: [REQUEST_OPTION]
        :end-before: [REQUEST_OPTION]
    """
    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    cfg.method = 'head'
    kwargs = get_request_kwargs(cfg, **kwargs)
    kwargs['stream']  = kwargs.get('stream', True)
    resp = requests.head(url, params=params, json=json, data=data, **kwargs)
    if cfg.http_success_only:
        resp.raise_for_status()
    return resp

def request(url, cfg=None, params=None, json=None, data=None, **kwargs):
    """Send request

    :return: :class:`Response <Response>` object
    :rtype: requests.Response

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :language: python
        :start-after: [REQUEST_OPTION]
        :end-before: [REQUEST_OPTION]
    """
    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    kwargs = get_request_kwargs(cfg, **kwargs)
    kwargs['stream']  = kwargs.get('stream', True)
    method  = 'get'
    if 'method' in kwargs:
        method = kwargs['method']
        del kwargs['method']
    resp = requests.request(method, url, params=params, json=json, data=data, **kwargs)
    if cfg.http_success_only:
        resp.raise_for_status()
    return resp

def get(url, cfg=None, **kwargs):
    """Raw GET method request

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :language: python
        :start-after: [REQUEST_OPTION]
        :end-before: [REQUEST_OPTION]
    """
    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    kwargs = get_request_kwargs(cfg, **kwargs)
    resp = requests.get(url, **kwargs)
    if cfg.http_success_only:
        resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp

def post(url, cfg=None, **kwargs):
    """Raw POST method request

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :language: python
        :start-after: [REQUEST_OPTION]
        :end-before: [REQUEST_OPTION]
    """
    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    kwargs = get_request_kwargs(cfg, **kwargs)
    resp = requests.post(url, **kwargs)
    if cfg.http_success_only:
        resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp

def get_html(url, cfg=None, **kwargs):
    """We handle error cases:

    - Attempt to find encoding of the html by using HTTP header. Fallback to 'ISO-8859-1' if not provided.
    - Error out if a non 2XX HTTP response code is returned.

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :language: python
        :start-after: [REQUEST_OPTION]
        :end-before: [REQUEST_OPTION]
    """

    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    kwargs = get_request_kwargs(cfg, **kwargs)
    method  = 'get'
    if 'method' in kwargs:
        method = kwargs['method']
        del kwargs['method']
    html = ''
    try:
        resp = requests.request(method, url, **kwargs)
        html = get_html_from_response(resp)
        if cfg.http_success_only:
            # fail if HTTP sends a non 2XX response
            resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error('[NETWORK] get_html() error. %s on URL: %s', e, url)
    return html

def get_html_from_response(response):
    FAIL_ENCODING = 'ISO-8859-1'
    if response.encoding != FAIL_ENCODING:
        # return response as a unicode string
        html = response.text
    else:
        html = response.content
        if 'charset' not in response.headers.get('content-type'):
            encodings = requests.utils.get_encodings_from_content(response.text)
            if len(encodings) > 0:
                response.encoding = encodings[0]
                html = response.text
    return html or ''

def get_soup(url, cfg=None, **kwargs):
    html = get_html(url, cfg, **kwargs)
    return BeautifulSoup(html, features='html.parser')

class MRequest(object):
    """Wrapper for request object for multithreading. If the domain we are
    crawling is under heavy load, the self.resp will be left as None.
    If this is the case, we still want to report the url which has failed
    so (perhaps) we can try again later.

    :meta private:
    """
    def __init__(self, method, url, cfg=None, params=None, json=None, data=None, proxies=None, **kwargs):
        self.url    = url
        self.cfg    = cfg
        self.method = method
        self.params = params
        self.json   = json
        self.data   = data
        self.proxies = proxies
        self.kwargs = kwargs
        self.resp   = None

    def send(self):
        try:
            self.resp = requests.request(
                self.method, self.url, params=self.params, json=self.json, data=self.data, proxies=self.proxies,
                **get_request_kwargs(**self.kwargs))
            if self.cfg.http_success_only:
                self.resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.critical('[NETWORK][REQUEST FAILED] ' + str(e))

# pylint: disable=no-member
def multithread_request(urls, cfg=None, method='get', params_list=None, json_list=None, data_list=None, proxy_list=None, **kwargs):
    """Request multiple urls via mthreading, order of urls & requests is stable
    returns same requests but with response variables filled.

    :param list[str] urls: Urls list
    :param dict cfg: Request config, see :ref:`HTTPUTILS_DEFAULT_CONFIG`
    :param list params_list: param list for each request
    :param list json_list: json list for each request
    :param list data_list: data list for each request
    :param list proxy_list: proxy list for each request

    :return: object
    :rtype: list[MRequest]

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :name: HTTPUTILS_DEFAULT_CONFIG
        :language: python
        :start-after: [DEFAULT_CONFIG]
        :end-before: [DEFAULT_CONFIG]

    .. literalinclude:: /../../tests/test_httputils.py
        :caption: Useage
        :language: python
        :pyobject: test_multithread_request
    """

    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    kwargs = get_request_kwargs(cfg, **kwargs)
    thread_num = cfg.thread_num
    timeout = cfg.thread_timeout
    pool = ThreadPool(thread_num, timeout)
    m_requests = []
    for i,url in enumerate(urls):
        params  = params_list[i] if params_list and i<len(params_list) else None
        json    = json_list[i] if json_list and i<len(json_list) else None
        data    = data_list[i] if data_list and i<len(data_list) else None
        proxies = proxy_list[i] if proxy_list and i<len(proxy_list) else None
        if 'proxies' in kwargs:
            del kwargs['proxies'] # ignore proxies settings in kwargs
        m_requests.append(MRequest(method, url, cfg, params, json, data, proxies=proxies, **kwargs))

    for req in m_requests:
        pool.add_task(req.send)

    pool.wait_completion()
    return m_requests

def download(url, cfg=None, outpath=None, isdir=False, **kwargs):
    """ Download file from url and save to outpath

    :param outpath: Output directory/file path. If dir, try get file name from header or system time will used. 
    :param bool isdir: outpath is dir or not.
    :return: output file path

    .. literalinclude:: /../../zwdata/utils/httputils.py
        :caption: Default config value
        :language: python
        :start-after: [REQUEST_OPTION]
        :end-before: [REQUEST_OPTION]

    .. literalinclude:: /../../tests/test_httputils.py
        :caption: Useage
        :language: python
        :pyobject: test_download
    """
    cfg = update_attrs(DEFAULT_CONFIG, cfg or {})
    kwargs = get_request_kwargs(cfg, **kwargs)
    kwargs['stream']  = kwargs.get('stream', True)
    method  = 'get'
    if 'method' in kwargs:
        method = kwargs['method']
        del kwargs['method']
    resp = requests.request(method, url, **kwargs)
    if cfg.http_success_only:
        # fail if HTTP sends a non 2XX response
        resp.raise_for_status()

    outpath = Path(outpath)
    if isdir:
        fname = None
        if 'content-disposition' in resp.headers:
            dis = resp.headers['content-disposition']
            arr = re.findall('filename=(.+)', dis)
            fname = arr[0].strip() if len(arr)>0 else None
            if fname:
                # enc = chardet.detect(str.encode(fname))
                # fname = fname.encode().decode('utf-8')
                fname = fname.encode('ISO-8859-1').decode('utf-8')
        fname = Path( fname or '%s' % int(time.time()) )
        outpath = outpath / ( '%s%s'%(fname.stem.strip(), fname.suffix) )
    outpath = outpath.resolve()
    outpath.parent.mkdir(parents=True, exist_ok=True)

    with open(str(outpath), 'wb') as f:
        for chunk in resp.iter_content(chunk_size=512 * 1024): 
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            #if chunk: 
            f.write(chunk)
    return outpath

def check_connect(urls):
    """Check url connection, return final url and test result

    :param list[str] urls: Urls to check
    :return: List of (final url,test result)
    :rtype: list[tuple]

    .. literalinclude:: /../../tests/test_httputils.py
        :caption: Useage
        :language: python
        :pyobject: test_check_connect
    """
    rtn = []
    for u in urls:
        r = (u, False)
        try:
            resp = head(u)
            status_code = resp.status_code
            if status_code == 200:
                r = (u, True)
            elif status_code == 301 or status_code == 302:
                url = resp.headers['Location']
                r = (url, True)
            elif status_code == 403:
                resp_get = requests.get(u)
                if resp_get.status_code == 200:
                    r = (u, True)
        except Exception:
            pass
        rtn.append(r)
    return rtn

def load_cookies(pth):
    """Load cookies from json file

    :param pth: cookies file path.
    :return: cookies jar or None
    :rtype: requests.cookies.RequestsCookieJar

    """

    jar = None
    cpth = Path(pth) if pth else None
    if cpth and cpth.exists():
        cookiesjson = readjson(cpth)
        jar = requests.cookies.cookiejar_from_dict(cookiesjson)
    return jar

def save_cookies(resp, pth):
    """Save cookies to json file

    :param dict resp: request response.
    :param pth:cookies file path.
    :return: True if save success
    :rtype: bool
    """
    if pth is None:
        return False
    cookiesjson = requests.utils.dict_from_cookiejar(resp.cookies) 
    writejson(pth, cookiesjson)
    return True

def is_empty_page(htmlstr, minsize=1000):
    """Check htmlstr whether is empty or not by content
    """
    emptyhtml = '<html><head></head><body></body></html>'
    canntopen = '无法访问此网站'
    openfail = '请检查您的代理服务器设置或与网络管理员联系'
    notfound = ['404 Not Found', 'HTTP状态 404']

    if htmlstr == emptyhtml or canntopen in htmlstr or openfail in htmlstr:
        return True
    for k in notfound:
        if k in htmlstr and len(htmlstr)<minsize:
            return True
    if len(htmlstr)<minsize:
        return True
    soup = BeautifulSoup(htmlstr, features='html.parser')
    if not soup.body:
        return True
    return False