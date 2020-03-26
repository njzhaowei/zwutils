import logging
import requests
from .mthreading import ThreadPool
from .comm import dict2attr
from .comm import update_attrs

FAIL_ENCODING = 'ISO-8859-1'

def get_request_kwargs(timeout, useragent, proxies, headers=None, cookies=None):
    """This Wrapper method exists b/c some values in req_kwargs dict
    are methods which need to be called every time we make a request
    """

    return {
        'headers': headers if headers else {'User-Agent': useragent},
        'cookies': cookies if cookies else {},
        'timeout': timeout,
        'allow_redirects': True,
        'proxies': proxies
    }

def get_html(url, settings=None, cookies=None, response=None):
    """HTTP response code agnostic
    """
    try:
        return get_html_2XX_only(url, settings, cookies, response)
    except requests.exceptions.RequestException as e:
        logging.error('[zwutils] get_html() error. %s on URL: %s', e, url)
        return ''

def get_html_2XX_only(url, settings=None, cookies=None, response=None):
    """Consolidated logic for http requests from gnews. We handle error cases:
    - Attempt to find encoding of the html by using HTTP header. Fallback to
      'ISO-8859-1' if not provided.
    - Error out if a non 2XX HTTP response code is returned.
    """
    useragent = settings.useragent
    timeout = settings.request_timeout
    proxies = settings.proxies
    headers = settings.headers

    if response is not None:
        return _get_html_from_response(response, settings)
    response = requests.get(
        url=url, **get_request_kwargs(timeout, useragent, proxies, headers, cookies))
    html = _get_html_from_response(response, settings)
    if settings.http_success_only:
        # fail if HTTP sends a non 2XX response
        response.raise_for_status()
    return html

def _get_html_from_response(response, settings):
    if response.headers.get('content-type') in settings.ignored_content_types_defaults:
        return settings.ignored_content_types_defaults[response.headers.get('content-type')]
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

class MRequest(object):
    """Wrapper for request object for multithreading. If the domain we are
    crawling is under heavy load, the self.resp will be left as None.
    If this is the case, we still want to report the url which has failed
    so (perhaps) we can try again later.
    """
    def __init__(self, url, settings=None, cookies=None):
        self.url = url
        self.settings = settings
        self.useragent = settings.useragent
        self.timeout = settings.request_timeout
        self.proxies = settings.proxies
        self.headers = settings.headers
        self.cookies = cookies
        self.resp = None

    def send(self):
        try:
            self.resp = requests.get(self.url, **get_request_kwargs(
                self.timeout, self.useragent, self.proxies, self.headers, self.cookies))
            if self.settings.http_success_only:
                self.resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.critical('[zwutils][REQUEST FAILED] ' + str(e))

# pylint: disable=no-member
def multithread_request(urls, settings=None, cookies=None):
    """Request multiple urls via mthreading, order of urls & requests is stable
    returns same requests but with response variables filled.

    thread_timeout: in seconds
    request_timeout: in seconds, 连接超时设为比3的倍数略大的一个数值
    """
    defaut_settings = {
        'thread_num': 5,
        'thread_timeout': 3,
        'request_timeout': 5,
        'headers': {},
        'proxies': {},
        'useragent': '',
        'http_success_only': True
    }
    settings = update_attrs(defaut_settings, settings)

    thread_num = settings.thread_num
    timeout = settings.thread_timeout
    pool = ThreadPool(thread_num, timeout)
    m_requests = []
    for url in urls:
        m_requests.append(MRequest(url, settings, cookies))

    for req in m_requests:
        pool.add_task(req.send)

    pool.wait_completion()
    return m_requests

